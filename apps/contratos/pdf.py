import io
import hashlib
import logging
import platform
import shutil
import subprocess
import tempfile
import threading
import time
from decimal import Decimal
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from django.conf import settings


logger = logging.getLogger(__name__)
_template_cache_lock = threading.Lock()


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


def _cached_docx_template(template_path):
    """Return a local DOCX template, converting legacy DOC files only once."""
    template_path = Path(template_path)
    cache_dir = Path(settings.MEDIA_ROOT) / "contratos" / "plantillas"
    cache_dir.mkdir(parents=True, exist_ok=True)
    stat = template_path.stat()
    fingerprint = "{}|{}|{}".format(
        str(template_path).casefold(), stat.st_mtime_ns, stat.st_size
    )
    digest = hashlib.sha256(fingerprint.encode("utf-8")).hexdigest()[:20]
    cached = cache_dir / "{}_{}{}.docx".format(
        template_path.stem[:60], digest, "_doc" if template_path.suffix.lower() == ".doc" else ""
    )
    if cached.is_file():
        return cached

    with _template_cache_lock:
        if cached.is_file():
            return cached
        with tempfile.TemporaryDirectory(
            prefix="agroservice_template_", dir=str(cache_dir)
        ) as temp:
            temp_dir = Path(temp)
            local_source = temp_dir / template_path.name
            shutil.copy2(str(template_path), str(local_source))
            if local_source.suffix.lower() == ".doc":
                converted = temp_dir / "template.docx"
                if platform.system() == "Windows":
                    _word_convert(local_source, converted)
                else:
                    executable = shutil.which("soffice") or shutil.which("libreoffice")
                    if not executable:
                        raise RuntimeError("LibreOffice es necesario para convertir la plantilla DOC.")
                    subprocess.run(
                        [executable, "--headless", "--convert-to", "docx", "--outdir", str(temp_dir), str(local_source)],
                        check=True,
                    )
                    generated = temp_dir / (local_source.stem + ".docx")
                    if generated != converted:
                        generated.replace(converted)
            elif local_source.suffix.lower() == ".docx":
                converted = local_source
            else:
                raise RuntimeError("La plantilla contractual debe estar en formato DOC o DOCX.")

            temporary = cache_dir / (cached.name + ".tmp")
            shutil.copy2(str(converted), str(temporary))
            temporary.replace(cached)
    return cached


def build_contract_pdf(template_path, data):
    started = time.perf_counter()
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

    template_started = time.perf_counter()
    source_template = _cached_docx_template(template_path)
    template_seconds = time.perf_counter() - template_started

    with tempfile.TemporaryDirectory(prefix="agroservice_contract_") as temp:
        temp_dir = Path(temp)
        source = temp_dir / "template.docx"
        shutil.copy2(str(source_template), str(source))
        merged = temp_dir / "contrato.docx"
        _replace_docx_fields(source, merged, values)
        pdf_path = temp_dir / "contrato.pdf"
        conversion_started = time.perf_counter()
        if platform.system() == "Windows":
            _word_convert(merged, pdf_path, pdf=True)
        else:
            _libreoffice_convert(merged, temp_dir)
        conversion_seconds = time.perf_counter() - conversion_started
        result = io.BytesIO(pdf_path.read_bytes())
        logger.info(
            "Contrato PDF generado: plantilla=%.3fs conversion=%.3fs total=%.3fs bytes=%s",
            template_seconds,
            conversion_seconds,
            time.perf_counter() - started,
            len(result.getbuffer()),
        )
        return result
