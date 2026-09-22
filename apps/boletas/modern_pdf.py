"""Diseño A4 compartido por las boletas mensuales y semanales de Nisira."""
from datetime import datetime
from io import BytesIO
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from .electronic_delivery_pdf import draw_delivery_footer
from .erg_txt import PayrollTextError, amount


GREEN = colors.HexColor("#08734a")
DARK_GREEN = colors.HexColor("#124b40")
INK = colors.HexColor("#172833")
PALE = colors.HexColor("#f0f8f5")
BORDER = colors.HexColor("#c6dfd5")
WHITE = colors.white
MONTHS = (
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "setiembre", "octubre", "noviembre", "diciembre",
)


def build_pdf(data, signature_path=None, employer_signature_path=None, delivery=None, weekly=False):
    header, details, totals = data["header"], data["details"], data["totals"]
    output = BytesIO()
    width, height = A4
    pdf = canvas.Canvas(output, pagesize=A4)
    pdf.setTitle("Boleta de remuneraciones {} {}".format(header.get("documento", ""), header.get("periodo", "")))
    pdf.setAuthor(header.get("razon_social") or "AGROSERVICE ICA SUR S.A.C.")
    regular, bold = _fonts()
    left, right = 7 * mm, width - 7 * mm

    def clean(value, default="-"):
        value = str(value).strip() if value is not None else ""
        return value or default

    def fit(value, max_width, size=8, font=None):
        font = font or regular
        value = clean(value)
        if pdf.stringWidth(value, font, size) <= max_width:
            return value
        while value and pdf.stringWidth(value + "…", font, size) > max_width:
            value = value[:-1]
        return value.rstrip() + "…"

    def text(x, y, value, size=8, font=None, color=INK, max_width=None):
        font = font or regular
        pdf.setFillColor(color)
        pdf.setFont(font, size)
        pdf.drawString(x, y, fit(value, max_width, size, font) if max_width else clean(value))

    def date(value):
        raw = clean(value, "")
        for pattern in ("%Y%m%d", "%Y-%m-%d", "%d/%m/%Y"):
            try:
                return datetime.strptime(raw[:10], pattern).strftime("%d/%m/%Y")
            except ValueError:
                continue
        return raw or "-"

    def money(value):
        return "{:,.2f}".format(amount(value or 0))

    def box(x, y, w, h, fill=WHITE, radius=1.5 * mm, stroke=BORDER):
        pdf.setFillColor(fill)
        pdf.setStrokeColor(stroke)
        pdf.setLineWidth(.45)
        pdf.roundRect(x, y, w, h, radius, fill=1, stroke=1)

    # Cabecera: logo institucional, período y fecha de autorización.
    logo = Path(__file__).resolve().parents[2] / "static" / "assets" / "img" / "logo" / "agroservice-corporativo.png"
    if logo.is_file():
        pdf.drawImage(str(logo), left, height - 39 * mm, 94 * mm, 31 * mm,
                      preserveAspectRatio=True, anchor="c", mask="auto")
    else:
        text(left, height - 23 * mm, "AGROSERVICE", 19, bold, DARK_GREEN)
    text(left + 44 * mm, height - 39 * mm, "ICA SUR S.A.C.", 10.5, bold)
    text(left + 44 * mm, height - 44 * mm, "R.U.C. {}".format(clean(header.get("ruc"), "20534627077")), 7.3)
    text(left, height - 51 * mm,
         clean(header.get("direccion_empresa"), "Car. Panamericana Sur Km. 297 - Ica - Ica - Subtanjalla - Perú"),
         6.8, max_width=right - left - 95 * mm)
    pdf.setStrokeColor(GREEN)
    pdf.setLineWidth(1)
    pdf.line(111 * mm, height - 49 * mm, 111 * mm, height - 11 * mm)
    text(116 * mm, height - 18 * mm, "BOLETA DE", 14, bold)
    text(116 * mm, height - 25 * mm, "REMUNERACIONES", 14, bold)
    box(116 * mm, height - 49 * mm, right - 116 * mm, 20 * mm, PALE)
    pdf.setStrokeColor(BORDER)
    pdf.line(162 * mm, height - 46 * mm, 162 * mm, height - 32 * mm)
    period_code = clean(header.get("periodo"), "")
    if len(period_code) >= 6 and period_code[4:6].isdigit() and 1 <= int(period_code[4:6]) <= 12:
        period_label = "{} {}".format(MONTHS[int(period_code[4:6]) - 1].capitalize(), period_code[:4])
    else:
        period_label = period_code or "Período"
    text(120 * mm, height - 34 * mm, "PERÍODO DE PAGO", 6.5, bold)
    text(120 * mm, height - 41 * mm, period_label, 11, bold, max_width=40 * mm)
    period_line = "Del {} al {}".format(date(header.get("desde1")), date(header.get("hasta1")))
    text(120 * mm, height - 46 * mm, period_line, 6.3, max_width=40 * mm)
    text(166 * mm, height - 34 * mm, "FECHA DE EMISIÓN", 6.3, bold)
    text(166 * mm, height - 41 * mm, (delivery or {}).get("issued_at") or "No registrada", 10.5, bold,
         max_width=right - 169 * mm)
    text(166 * mm, height - 46 * mm, "Ica, Perú", 6.5)

    # Ficha del trabajador.
    worker_bottom, worker_height = 204 * mm, 39 * mm
    box(left, worker_bottom, right - left, worker_height)
    pdf.setFillColor(PALE)
    pdf.roundRect(left, worker_bottom + worker_height - 8 * mm, right - left, 8 * mm,
                  1.5 * mm, fill=1, stroke=0)
    text(left + 4 * mm, worker_bottom + worker_height - 5.5 * mm,
         "DATOS DEL TRABAJADOR", 8.3, bold)
    pdf.setStrokeColor(BORDER)
    pdf.line(width / 2, worker_bottom + 3 * mm, width / 2, worker_bottom + 30 * mm)
    code = clean(header.get("codigo") or header.get("documento"))
    affiliate = "{} {}".format(clean(header.get("afp"), ""), clean(header.get("afp_dsc"), "")).strip() or "-"
    left_rows = (
        ("Código", code), ("Nombres", header.get("apenom")),
        ("Cargo", header.get("cargo")),
        ("Área", header.get("area") or header.get("descripcion_area")),
        ("AFP", affiliate),
    )
    right_rows = (
        ("DNI", header.get("documento")),
        ("CUSSP/ONP", "{} {}".format(clean(header.get("autogene"), ""), clean(header.get("autoipss"), "")).strip() or "-"),
        ("Situación", header.get("situacion_especial") or "Ninguno"),
        ("Fec. Ingreso", date(header.get("ingreso"))),
        ("Fec. Cese", date(header.get("cese"))),
    )
    for index, (label, value) in enumerate(left_rows):
        y = worker_bottom + 27.5 * mm - index * 5.1 * mm
        text(left + 4 * mm, y, label, 7.2)
        text(left + 21 * mm, y, ":", 7.2)
        text(left + 27 * mm, y, value, 7.2, bold, max_width=width / 2 - left - 31 * mm)
    for index, (label, value) in enumerate(right_rows):
        y = worker_bottom + 27.5 * mm - index * 5.1 * mm
        text(width / 2 + 6 * mm, y, label, 7.2)
        text(width / 2 + 27 * mm, y, ":", 7.2)
        text(width / 2 + 33 * mm, y, value, 7.2, bold, max_width=right - width / 2 - 37 * mm)

    # Cuatro columnas con encabezados verdes y filas de conceptos.
    table_top = 201 * mm
    table_bottom = (126 if weekly else 106) * mm
    gap = 2 * mm
    column_width = (right - left - 3 * gap) / 4
    sections = (
        (("REMUNERACIONES",), "Ingresos por tu trabajo", "ingr", GREEN),
        (("RETENCIONES AL", "TRABAJADOR"), "Descuentos de ley", "desc", DARK_GREEN),
        (("CONTRIBUCIONES DEL", "EMPLEADOR"), "Aportes por tu trabajo", "apor", GREEN),
        (("TIEMPOS",), "Resumen del período", "tiem", DARK_GREEN),
    )
    row_height = (3.0 if weekly else 3.4) * mm
    max_rows = int((table_top - table_bottom - 24 * mm) // row_height)
    for index, (titles, subtitle, prefix, color) in enumerate(sections):
        x = left + index * (column_width + gap)
        box(x, table_bottom, column_width, table_top - table_bottom)
        pdf.setFillColor(color)
        pdf.roundRect(x, table_top - 17 * mm, column_width, 17 * mm, 1.5 * mm, fill=1, stroke=0)
        for title_index, title in enumerate(titles):
            text(x + 3 * mm, table_top - (6.2 + title_index * 3.5) * mm,
                 title, 7.1, bold, WHITE, column_width - 6 * mm)
        text(x + 3 * mm, table_top - (14 if len(titles) > 1 else 12.5) * mm,
             subtitle, 6.2, regular, WHITE, column_width - 6 * mm)
        pdf.setFillColor(PALE)
        pdf.rect(x, table_top - 24 * mm, column_width, 7 * mm, fill=1, stroke=0)
        text(x + 3 * mm, table_top - 21.5 * mm, "Concepto", 6.6, bold)
        pdf.setFillColor(INK)
        pdf.setFont(bold, 6.6)
        pdf.drawRightString(x + column_width - 2 * mm, table_top - 21.5 * mm,
                            "Horas" if prefix == "tiem" else "Monto (S/.)")
        concepts = [
            (clean(row.get(prefix + "_descri"), ""), row.get(prefix + "_valor"))
            for row in details if clean(row.get(prefix + "_descri"), "")
        ]
        if len(concepts) > max_rows:
            raise PayrollTextError("Los conceptos exceden el espacio del formato de boleta.")
        for row_index, (label, value) in enumerate(concepts):
            y = table_top - 24 * mm - (row_index + 1) * row_height
            if row_index % 2:
                pdf.setFillColor(colors.HexColor("#f8fbfa"))
                pdf.rect(x + .4 * mm, y, column_width - .8 * mm, row_height, fill=1, stroke=0)
            text(x + 2 * mm, y + 1.1 * mm, label, 6.2, max_width=column_width - 19 * mm)
            pdf.setFillColor(INK)
            pdf.setFont(regular, 6.2)
            pdf.drawRightString(x + column_width - 2 * mm, y + 1.1 * mm, money(value))

    if weekly:
        _daily_detail(pdf, data.get("daily_details") or [], left, right, regular, bold)

    # Totales, observaciones y firmas.
    totals_y = 89 * mm
    total_labels = ("TOTAL INGRESOS", "TOTAL RETENCIONES", "TOTAL APORTACIÓN", "NETO A PAGAR")
    for index, (label, key) in enumerate(zip(total_labels, ("ingr", "desc", "apor", "net"))):
        x = left + index * (column_width + gap)
        box(x, totals_y, column_width, 14 * mm, GREEN if index == 3 else PALE,
            stroke=GREEN if index == 3 else BORDER)
        text(x + 3 * mm, totals_y + 9 * mm, label, 6.6, bold, WHITE if index == 3 else INK)
        text(x + 3 * mm, totals_y + 2.5 * mm, "S/ " + money(totals[key]), 12, bold,
             WHITE if index == 3 else INK, column_width - 6 * mm)
    box(left, 76 * mm, right - left, 10 * mm, PALE)
    text(left + 4 * mm, 80 * mm, "OBSERVACIONES", 7.3, bold)
    text(left + 33 * mm, 80 * mm, header.get("observaciones") or "-", 7.1,
         max_width=right - left - 38 * mm)

    pdf.setStrokeColor(BORDER)
    pdf.line(width / 2, 39 * mm, width / 2, 70 * mm)
    employer_center, worker_center = 56 * mm, 155 * mm
    if employer_signature_path:
        try:
            pdf.drawImage(employer_signature_path, employer_center - 25 * mm, 48 * mm, 50 * mm, 20 * mm,
                          preserveAspectRatio=True, anchor="c", mask="auto")
        except Exception as exc:
            raise PayrollTextError("No se pudo insertar la firma del empleador en la boleta.") from exc
    if signature_path:
        try:
            pdf.drawImage(signature_path, worker_center - 25 * mm, 48 * mm, 50 * mm, 20 * mm,
                          preserveAspectRatio=True, anchor="c", mask="auto")
        except Exception as exc:
            raise PayrollTextError("No se pudo insertar la firma registrada en la boleta.") from exc
    pdf.setStrokeColor(DARK_GREEN)
    pdf.line(25 * mm, 47 * mm, 87 * mm, 47 * mm)
    pdf.line(123 * mm, 47 * mm, 187 * mm, 47 * mm)
    pdf.setFillColor(INK)
    pdf.setFont(bold, 7)
    pdf.drawCentredString(employer_center, 42 * mm, "MARTÍNEZ BERRÍOS LUIS FERNANDO")
    pdf.drawCentredString(worker_center, 42 * mm, "TRABAJADOR")
    pdf.setFont(regular, 6.8)
    pdf.drawCentredString(employer_center, 38 * mm, "GERENTE GENERAL")
    pdf.drawCentredString(worker_center, 38 * mm, fit(header.get("apenom"), 57 * mm, 6.8))

    draw_delivery_footer(pdf, left, right, delivery, qr_data="{}|{}|{}".format(
        clean(header.get("ruc"), "20534627077"), clean(header.get("documento")),
        clean(header.get("periodo")),
    ))
    pdf.showPage()
    pdf.save()
    return output.getvalue()


def _fonts():
    folder = Path("C:/Windows/Fonts")
    if (folder / "arial.ttf").is_file() and (folder / "arialbd.ttf").is_file():
        if "Payslip-Arial" not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont("Payslip-Arial", str(folder / "arial.ttf")))
            pdfmetrics.registerFont(TTFont("Payslip-Arial-Bold", str(folder / "arialbd.ttf")))
        return "Payslip-Arial", "Payslip-Arial-Bold"
    return "Helvetica", "Helvetica-Bold"


def _daily_detail(pdf, rows, left, right, regular, bold):
    rows = list(rows)
    if len(rows) > 7:
        raise PayrollTextError("El detalle diario excede siete días.")
    bottom, top = 106 * mm, 123 * mm
    pdf.setFillColor(PALE)
    pdf.setStrokeColor(BORDER)
    pdf.roundRect(left, bottom, right - left, top - bottom, 1.5 * mm, fill=1, stroke=1)
    pdf.setFillColor(INK)
    pdf.setFont(bold, 6.2)
    pdf.drawString(left + 3 * mm, top - 3.5 * mm, "DETALLE DIARIO")
    starts = (left + 43 * mm, left + 89 * mm, left + 135 * mm)
    for x, heading in zip(starts, ("Día / Fecha", "Horas", "Rendimiento")):
        pdf.drawString(x, top - 3.5 * mm, heading)
    for index, row in enumerate(rows):
        y = top - (5.3 + index * 1.65) * mm
        day = str(row.get("day") or "")[:2].upper()
        raw_date = str(row.get("date") or "")
        try:
            formatted = datetime.strptime(raw_date, "%Y%m%d").strftime("%d/%m/%Y")
        except ValueError:
            formatted = raw_date
        pdf.setFont(regular, 5.4)
        pdf.drawString(left + 3 * mm, y, "{} {}".format(day, formatted))
        pdf.drawString(starts[1], y, str(row.get("hours") or "-"))
        pdf.drawString(starts[2], y, str(row.get("performance") or "-"))
