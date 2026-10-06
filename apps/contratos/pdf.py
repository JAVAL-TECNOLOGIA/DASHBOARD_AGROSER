import io
import platform
import shutil
import subprocess
import tempfile
from decimal import Decimal
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


MONTHS = (
    "", "ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO",
    "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE",
)


def _amount_in_words(value):
    amount = Decimal(value or 0).quantize(Decimal("0.01"))
    integer = int(amount)
    cents = int((amount - integer) * 100)
    units = (
        "CERO", "UNO", "DOS", "TRES", "CUATRO", "CINCO", "SEIS", "SIETE",
        "OCHO", "NUEVE", "DIEZ", "ONCE", "DOCE", "TRECE", "CATORCE",
        "QUINCE", "DIECISEIS", "DIECISIETE", "DIECIOCHO", "DIECINUEVE",
        "VEINTE", "VEINTIUNO", "VEINTIDOS", "VEINTITRES", "VEINTICUATRO",
        "VEINTICINCO", "VEINTISEIS", "VEINTISIETE", "VEINTIOCHO", "VEINTINUEVE",
    )
    tens = ("", "", "VEINTE", "TREINTA", "CUARENTA", "CINCUENTA", "SESENTA", "SETENTA", "OCHENTA", "NOVENTA")
    hundreds = ("", "CIENTO", "DOSCIENTOS", "TRESCIENTOS", "CUATROCIENTOS", "QUINIENTOS", "SEISCIENTOS", "SETECIENTOS", "OCHOCIENTOS", "NOVECIENTOS")

    def under_thousand(number):
        if number == 100:
            return "CIEN"
        parts = []
        if number >= 100:
            parts.append(hundreds[number // 100])
            number %= 100
        if number < 30:
            if number:
                parts.append(units[number])
        else:
            word = tens[number // 10]
            if number % 10:
                word += " Y " + units[number % 10]
            parts.append(word)
        return " ".join(parts)

    if integer < 1000:
        words = under_thousand(integer)
    elif integer < 1000000:
        thousands, remainder = divmod(integer, 1000)
        prefix = "MIL" if thousands == 1 else under_thousand(thousands) + " MIL"
        words = prefix + ((" " + under_thousand(remainder)) if remainder else "")
    else:
        words = str(integer)
    return "({} CON {:02d}/100)".format(words, cents)


def _replace_docx_fields(source, destination, values):
    with ZipFile(str(source)) as src, ZipFile(str(destination), "w", ZIP_DEFLATED) as dst:
        for item in src.infolist():
            data = src.read(item.filename)
            if item.filename.endswith(".xml"):
                xml = data.decode("utf-8")
                for field, value in values.items():
                    xml = xml.replace("«{}»".format(field), str(value or ""))
                data = xml.encode("utf-8")
            dst.writestr(item, data)


def _word_convert(source, destination, pdf=False):
    try:
        import pythoncom
        import win32com.client
    except ImportError:
        script = source.parent / "convert_contract.ps1"
        script.write_text(
            "$ErrorActionPreference = 'Stop'\n"
            "$word = New-Object -ComObject Word.Application\n"
            "$word.Visible = $false\n"
            "$word.DisplayAlerts = 0\n"
            "try {\n"
            "  $doc = $word.Documents.Open($args[0], $false, $true)\n"
            "  try { $doc.SaveAs2($args[1], [int]$args[2]) } finally { $doc.Close($false) }\n"
            "} finally { $word.Quit() }\n",
            encoding="utf-8",
        )
        result = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass",
             "-File", str(script), str(source.resolve()), str(destination.resolve()),
             "17" if pdf else "16"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if result.returncode:
            raise RuntimeError(result.stderr.strip() or "Microsoft Word no pudo convertir el contrato.")
        return

    pythoncom.CoInitialize()
    word = None
    document = None
    try:
        word = win32com.client.DispatchEx("Word.Application")
        word.Visible = False
        word.DisplayAlerts = 0
        document = word.Documents.Open(str(source.resolve()), ReadOnly=True)
        document.SaveAs(str(destination.resolve()), FileFormat=17 if pdf else 16)
    finally:
        if document is not None:
            document.Close(False)
        if word is not None:
            word.Quit()
        pythoncom.CoUninitialize()


def _libreoffice_convert(source, destination_dir):
    executable = shutil.which("soffice") or shutil.which("libreoffice")
    if not executable:
        raise RuntimeError("No se encontró Microsoft Word ni LibreOffice para generar el PDF.")
    subprocess.run(
        [executable, "--headless", "--convert-to", "pdf", "--outdir", str(destination_dir), str(source)],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def build_contract_pdf(template_path, data):
    start = data["inicio_contrato"]
    end = data["final_contrato"]
    address = ", ".join(filter(None, [data.get("address"), data.get("address_reference")]))
    basic = Decimal(data.get("basico") or 0).quantize(Decimal("0.01"))
    values = {
        "tbr_nombre": data.get("full_name"),
        "tbr_dni": data.get("document"),
        "tbr_sexo": "FEMENINO" if str(data.get("sexo", "")).upper().startswith("F") else "MASCULINO",
        "tbr_direcc": address,
        "tbr_dist": data.get("district"),
        "tbr_prov": data.get("province"),
        "tbr_dpto": data.get("department"),
        "tbr_cargo": data.get("position"),
        "cnt_diai": start.strftime("%d"),
        "cnt_mesi": MONTHS[start.month],
        "cnt_anoi": start.strftime("%Y"),
        "cnt_diaf": end.strftime("%d"),
        "cnt_mesf": MONTHS[end.month],
        "cnt_anof": end.strftime("%Y"),
        "tbr_rem_diaria": "{:,.2f}".format(basic),
        "tbr_rem_diariad": _amount_in_words(basic),
    }

    with tempfile.TemporaryDirectory(prefix="agroservice_contract_") as temp:
        temp_dir = Path(temp)
        source = temp_dir / template_path.name
        shutil.copy2(str(template_path), str(source))
        if source.suffix.lower() == ".doc":
            converted = temp_dir / "template.docx"
            if platform.system() == "Windows":
                _word_convert(source, converted)
            else:
                executable = shutil.which("soffice") or shutil.which("libreoffice")
                if not executable:
                    raise RuntimeError("LibreOffice es necesario para convertir la plantilla DOC.")
                subprocess.run([executable, "--headless", "--convert-to", "docx", "--outdir", str(temp_dir), str(source)], check=True)
                generated = temp_dir / (source.stem + ".docx")
                if generated != converted:
                    generated.replace(converted)
            source = converted
        if source.suffix.lower() != ".docx":
            raise RuntimeError("La plantilla contractual debe estar en formato DOC o DOCX.")

        merged = temp_dir / "contrato.docx"
        _replace_docx_fields(source, merged, values)
        pdf_path = temp_dir / "contrato.pdf"
        if platform.system() == "Windows":
            _word_convert(merged, pdf_path, pdf=True)
        else:
            _libreoffice_convert(merged, temp_dir)
        return io.BytesIO(pdf_path.read_bytes())
