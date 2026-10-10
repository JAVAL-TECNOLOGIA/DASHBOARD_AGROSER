import io
import hashlib
import logging
import platform
import shutil
import subprocess
import tempfile
import threading
import time
import json
import queue
import atexit
import sys
from decimal import Decimal
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from django.conf import settings


logger = logging.getLogger(__name__)
_template_cache_lock = threading.Lock()
_word_conversion_lock = threading.Lock()


class _WordConversionWorker:
    """Own one Word COM instance in a dedicated thread and reuse it."""

    def __init__(self):
        self._queue = queue.Queue()
        self._start_lock = threading.Lock()
        self._thread = None

    def warm(self):
        with self._start_lock:
            if self._thread is None or not self._thread.is_alive():
                self._thread = threading.Thread(
                    target=self._run,
                    name="contract-word-converter",
                    daemon=True,
                )
                self._thread.start()

    def convert_many(self, pairs, timeout=300):
        self.warm()
        response = queue.Queue(maxsize=1)
        self._queue.put(("convert", list(pairs), response))
        try:
            error = response.get(timeout=timeout)
        except queue.Empty:
            raise RuntimeError("Microsoft Word excedió el tiempo de generación del contrato.")
        if error is not None:
            raise error

    def stop(self):
        thread = self._thread
        if thread is not None and thread.is_alive():
            self._queue.put(("stop", (), None))
            thread.join(timeout=5)

    def _run(self):
        try:
            import pythoncom
            import win32com.client
        except ImportError:
            # The public conversion methods retain the PowerShell fallback.
            return

        pythoncom.CoInitialize()
        word = None
        startup_error = None
        try:
            try:
                word = win32com.client.DispatchEx("Word.Application")
                word.Visible = False
                word.DisplayAlerts = 0
            except Exception as exc:
                startup_error = exc
                logger.exception("No se pudo precargar Microsoft Word.")

            while True:
                action, pairs, response = self._queue.get()
                if action == "stop":
                    break
                error = startup_error
                if error is None:
                    try:
                        for source, destination, file_format in pairs:
                            document = word.Documents.Open(
                                str(Path(source).resolve()), ReadOnly=True
                            )
                            try:
                                document.SaveAs(
                                    str(Path(destination).resolve()),
                                    FileFormat=file_format,
                                )
                            finally:
                                document.Close(False)
                    except Exception as exc:
                        logger.exception("Microsoft Word no pudo convertir el contrato.")
                        error = exc
                response.put(error)
        finally:
            if word is not None:
                try:
                    word.Quit()
                except Exception:
                    logger.exception("No se pudo cerrar Microsoft Word correctamente.")
            pythoncom.CoUninitialize()


_word_worker = _WordConversionWorker()
atexit.register(_word_worker.stop)


def warm_contract_pdf_converter():
    """Start Word asynchronously while the user reviews the dashboard."""
    if "test" in sys.argv:
        return False
    if platform.system() == "Windows":
        try:
            import pythoncom  # noqa: F401
            import win32com.client  # noqa: F401
        except ImportError:
            return False
        _word_worker.warm()
        return True
    return False


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


def _word_convert_unlocked(source, destination, pdf=False):
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


def _word_convert(source, destination, pdf=False):
    try:
        import pythoncom  # noqa: F401
        import win32com.client  # noqa: F401
    except ImportError:
        with _word_conversion_lock:
            return _word_convert_unlocked(source, destination, pdf=pdf)
    _word_worker.convert_many([(source, destination, 17 if pdf else 16)])


def _word_convert_legacy(source, destination, pdf=False):
    with _word_conversion_lock:
        return _word_convert_unlocked(source, destination, pdf=pdf)


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


def _word_convert_many(pairs):
    """Convert several DOCX files with a single Microsoft Word process."""
    try:
        import pythoncom  # noqa: F401
        import win32com.client  # noqa: F401
    except ImportError:
        with _word_conversion_lock:
            return _word_convert_many_unlocked(pairs)
    _word_worker.convert_many([(source, destination, 17) for source, destination in pairs])


def _word_convert_many_legacy(pairs):
    with _word_conversion_lock:
        return _word_convert_many_unlocked(pairs)


def _word_convert_many_unlocked(pairs):
    try:
        import pythoncom
        import win32com.client
    except ImportError:
        work_dir = Path(pairs[0][0]).parent
        manifest = work_dir / "contracts.json"
        script = work_dir / "convert_contracts.ps1"
        manifest.write_text(
            json.dumps([{"source": str(Path(src).resolve()), "destination": str(Path(dst).resolve())} for src, dst in pairs]),
            encoding="utf-8",
        )
        script.write_text(
            "$ErrorActionPreference = 'Stop'\n"
            "$items = Get-Content -Raw -LiteralPath $args[0] | ConvertFrom-Json\n"
            "$word = New-Object -ComObject Word.Application\n"
            "$word.Visible = $false\n"
            "$word.DisplayAlerts = 0\n"
            "try {\n"
            "  foreach ($item in $items) {\n"
            "    $doc = $word.Documents.Open($item.source, $false, $true)\n"
            "    try { $doc.SaveAs2($item.destination, 17) } finally { $doc.Close($false) }\n"
            "  }\n"
            "} finally { $word.Quit() }\n",
            encoding="utf-8",
        )
        result = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-File", str(script), str(manifest)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if result.returncode:
            raise RuntimeError(result.stderr.strip() or "Microsoft Word no pudo convertir el lote.")
        return

    pythoncom.CoInitialize()
    word = None
    try:
        word = win32com.client.DispatchEx("Word.Application")
        word.Visible = False
        word.DisplayAlerts = 0
        for source, destination in pairs:
            document = word.Documents.Open(str(Path(source).resolve()), ReadOnly=True)
            try:
                document.SaveAs(str(Path(destination).resolve()), FileFormat=17)
            finally:
                document.Close(False)
    finally:
        if word is not None:
            word.Quit()
        pythoncom.CoUninitialize()


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


def _contract_values(data):
    start = data["inicio_contrato"]
    end = data["final_contrato"]
    address = ", ".join(filter(None, [data.get("address"), data.get("address_reference")]))
    basic = Decimal(data.get("basico") or 0).quantize(Decimal("0.01"))
    return {
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


def build_contract_pdf(template_path, data):
    started = time.perf_counter()
    values = _contract_values(data)

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


def build_contract_pdfs_batch(jobs):
    """Generate multiple contracts while starting Microsoft Word only once."""
    if not jobs:
        return 0
    started = time.perf_counter()
    work_root = Path(settings.MEDIA_ROOT) / "contratos" / "tmp"
    work_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
        prefix="agroservice_contract_batch_", dir=str(work_root)
    ) as temp:
        temp_dir = Path(temp)
        pairs = []
        outputs = []
        for index, job in enumerate(jobs):
            source_template = _cached_docx_template(job["template_path"])
            job_dir = temp_dir / str(index)
            job_dir.mkdir()
            merged = job_dir / "contrato.docx"
            _replace_docx_fields(source_template, merged, _contract_values(job["data"]))
            temporary_pdf = job_dir / "contrato.pdf"
            pairs.append((merged, temporary_pdf))
            outputs.append((temporary_pdf, Path(job["output_path"])))

        if platform.system() == "Windows":
            _word_convert_many(pairs)
        else:
            for source, _destination in pairs:
                _libreoffice_convert(source, source.parent)

        for temporary_pdf, output_path in outputs:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            temporary_output = output_path.with_suffix(".pdf.tmp")
            shutil.copy2(str(temporary_pdf), str(temporary_output))
            temporary_output.replace(output_path)
    logger.info(
        "Lote de contratos generado: cantidad=%s total=%.3fs promedio=%.3fs",
        len(jobs),
        time.perf_counter() - started,
        (time.perf_counter() - started) / len(jobs),
    )
    return len(jobs)
