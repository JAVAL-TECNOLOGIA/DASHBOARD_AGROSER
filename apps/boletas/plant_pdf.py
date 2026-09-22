"""Formato semanal de boleta para Obreros Planta y Planta General."""
from datetime import datetime
from decimal import Decimal
from io import BytesIO
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from .erg_txt import PayrollTextError, amount
from .electronic_delivery_pdf import draw_delivery_footer


MONTHS = (
    "ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO",
    "JULIO", "AGOSTO", "SETIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE",
)
DAY_NAMES = {
    "LUNES": "LU", "MARTES": "MA", "MIERCOLES": "MI", "MIÉRCOLES": "MI",
    "JUEVES": "JU", "VIERNES": "VI", "SABADO": "SA", "SÁBADO": "SA",
    "DOMINGO": "DO",
}


def build_pdf(data, signature_path=None, employer_signature_path=None, delivery=None):
    header, details, totals = data["header"], data["details"], data["totals"]
    output = BytesIO()
    width, height = A4
    pdf = canvas.Canvas(output, pagesize=A4)
    pdf.setTitle("Boleta semanal {}".format(header.get("documento", "")))
    pdf.setAuthor(header.get("razon_social", "AGROSERVICE ICA SUR S.A.C."))

    regular, bold = "Helvetica", "Helvetica-Bold"
    fonts = Path("C:/Windows/Fonts")
    if (fonts / "arial.ttf").is_file() and (fonts / "arialbd.ttf").is_file():
        if "Plant-Arial" not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont("Plant-Arial", str(fonts / "arial.ttf")))
            pdfmetrics.registerFont(TTFont("Plant-Arial-Bold", str(fonts / "arialbd.ttf")))
        regular, bold = "Plant-Arial", "Plant-Arial-Bold"

    left, right = 7 * mm, width - 7 * mm
    content_width = right - left

    def clean(value, default=""):
        return str(value).strip() if value not in (None, "") else default

    def money(value):
        return "{:,.2f}".format(amount(value or 0))

    def short_number(value):
        number = amount(value or 0)
        if not number:
            return ""
        return "{:.2f}".format(number)

    def display_date(value):
        try:
            return datetime.strptime(clean(value), "%Y%m%d").strftime("%d/%m/%Y")
        except ValueError:
            return clean(value, "-")

    def fit(value, available, font=regular, size=6.2):
        original = clean(value, "-")
        value = original
        while len(value) > 1 and pdf.stringWidth(value, font, size) > available:
            value = value[:-1]
        return value if value == original else value.rstrip() + "..."

    def centered_underlined(text, y, size):
        pdf.setFont(bold, size)
        pdf.drawCentredString(width / 2, y, text)
        text_width = pdf.stringWidth(text, bold, size)
        pdf.setLineWidth(0.35)
        pdf.line((width - text_width) / 2, y - 0.8 * mm, (width + text_width) / 2, y - 0.8 * mm)

    company_x = 42 * mm
    y = height - 14 * mm
    pdf.setFont(bold, 10)
    pdf.drawString(company_x, y, clean(header.get("razon_social"), "AGROSERVICE ICA SUR S.A.C."))
    pdf.setFont(regular, 5.5)
    pdf.drawString(company_x, y - 4.2 * mm, fit(header.get("direccion_empresa"), 125 * mm, size=5.5))
    pdf.setFont(bold, 12)
    pdf.drawString(company_x, y - 10.2 * mm, "R.U.C : {}".format(clean(header.get("ruc"), "20534627077")))

    centered_underlined("BOLETA DE REMUNERACIONES", height - 39 * mm, 9.5)
    payroll_type = clean(header.get("payroll_type"), "OBP").upper()
    subtitle = "OBREROS REGIMEN GENERAL" if payroll_type == "OBR" else "OBREROS REGIMEN AGRARIO LEY 31110"
    pdf.setFont(regular, 8.3)
    pdf.drawCentredString(width / 2, height - 44.5 * mm, subtitle)

    period_value = clean(header.get("periodo"), "000000")
    try:
        month_title = "{} {}".format(MONTHS[int(period_value[4:6]) - 1], period_value[:4])
    except (ValueError, IndexError):
        month_title = period_value
    pdf.setFont(bold, 9)
    pdf.drawCentredString(width / 2, height - 50 * mm, "Mes : {}".format(month_title))

    week_value = clean(header.get("payroll_week") or header.get("semana") or header.get("semana1"), "-")
    week_parts = [part for part in week_value.replace("-", "+").split("+") if part]
    week_from = week_parts[0] if week_parts else week_value
    week_to = week_parts[-1] if week_parts else week_value
    pdf.setFont(bold, 8.2)
    pdf.drawCentredString(
        width / 2,
        height - 56 * mm,
        "De Semana :  {}  desde  {}   /   A Semana :  {}  hasta  {}".format(
            week_from,
            display_date(header.get("desde1")),
            week_to,
            display_date(header.get("hasta1")),
        ),
    )

    info_top = height - 66 * mm
    info_left_value = left + 25 * mm
    info_right = left + 123 * mm
    info_right_value = info_right + 34 * mm

    def info_line(label, value, x_label, x_value, line_y, value_width):
        pdf.setFont(bold, 7.4)
        pdf.drawString(x_label, line_y, label)
        pdf.setFont(regular, 7.4)
        pdf.drawString(x_value, line_y, fit(value, value_width, regular, 7.4))

    affiliate = "{} - {}".format(clean(header.get("afp")), clean(header.get("afp_dsc"))).strip(" -")
    social_security = clean(header.get("ipss"), "ESSALUD -")
    left_rows = (
        ("NOMBRES", header.get("apenom")),
        ("CARGO", header.get("cargo")),
        ("AFILIADO", affiliate),
        ("SEGURO SOCIAL", social_security),
    )
    right_rows = (
        ("NRO. DOC.", header.get("documento")),
        ("BCP", header.get("cta_banco")),
        ("F. INGRESO", display_date(header.get("ingreso"))),
        ("REM. BAS.", money(header.get("basico"))),
    )
    for index, ((left_label, left_value), (right_label, right_value)) in enumerate(zip(left_rows, right_rows)):
        row_y = info_top - index * 6.3 * mm
        info_line(left_label, left_value, left, info_left_value, row_y, 91 * mm)
        info_line(right_label, right_value, info_right, info_right_value, row_y, right - info_right_value)

    table_top = height - 91 * mm
    table_bottom = 93 * mm
    header_height = 7 * mm
    column_width = content_width / 4
    headers = (("INGRESOS", "ingr"), ("DESCUENTOS", "desc"), ("APORTES EMPLEADOR", "apor"), ("TIEMPOS", "tiem"))
    pdf.setLineWidth(0.45)
    pdf.rect(left, table_bottom, content_width, table_top - table_bottom)
    pdf.line(left, table_top - header_height, right, table_top - header_height)
    for index, (title, prefix) in enumerate(headers):
        x = left + index * column_width
        if index:
            pdf.line(x, table_bottom, x, table_top)
        pdf.setFont(bold, 7.2)
        pdf.drawCentredString(x + column_width / 2, table_top - 4.5 * mm, title)
        concept_rows = [
            (clean(row.get(prefix + "_descri")), row.get(prefix + "_valor"))
            for row in details if clean(row.get(prefix + "_descri"))
        ]
        if len(concept_rows) > 17:
            raise PayrollTextError("Los conceptos exceden el espacio del formato semanal.")
        font_size = 5.5 if len(concept_rows) <= 13 else 4.8
        row_step = 5.7 * mm if len(concept_rows) <= 13 else 4.5 * mm
        row_y = table_top - header_height - 5.5 * mm
        for description, value in concept_rows:
            pdf.setFont(regular, font_size)
            pdf.drawString(x + 1 * mm, row_y, fit(description, column_width - 15 * mm, regular, font_size))
            pdf.drawRightString(x + column_width - 1 * mm, row_y, money(value))
            row_y -= row_step

    totals_top = table_bottom
    totals_bottom = totals_top - 15 * mm
    pdf.rect(left, totals_bottom, content_width, totals_top - totals_bottom)
    for index in range(1, 4):
        pdf.line(left + index * column_width, totals_bottom, left + index * column_width, totals_top)
    total_rows = (
        ("TOTAL INGRESOS", totals["ingr"]),
        ("TOTAL DESCUENTOS", totals["desc"]),
        ("TOTAL APORTES", totals["apor"]),
        ("Neto a Pagar:", totals["net"]),
    )
    for index, (label, value) in enumerate(total_rows):
        x = left + index * column_width
        pdf.setFont(bold if index == 3 else regular, 8.2 if index == 3 else 7.2)
        pdf.drawString(x + 1.2 * mm, totals_top - 5.2 * mm, label)
        if index == 3:
            pdf.setFont(regular, 7)
            pdf.drawString(x + 1.2 * mm, totals_bottom + 3.2 * mm, "S/")
            pdf.setFont(bold, 13)
        else:
            pdf.setFont(bold, 7.5)
        pdf.drawRightString(x + column_width - 1.2 * mm, totals_bottom + 3.2 * mm, money(value))

    detail_left = left
    detail_right = left + 98 * mm
    detail_top = totals_bottom - 2 * mm
    daily_rows = list(data.get("daily_details") or [])[:7]
    detail_header = 7 * mm
    detail_row_height = 5.1 * mm
    detail_total_height = 7 * mm
    detail_bottom = detail_top - detail_header - max(7, len(daily_rows)) * detail_row_height - detail_total_height
    detail_widths = (11 * mm, 34 * mm, 27 * mm, detail_right - detail_left - 72 * mm)
    pdf.rect(detail_left, detail_bottom, detail_right - detail_left, detail_top - detail_bottom)
    pdf.line(detail_left, detail_top - detail_header, detail_right, detail_top - detail_header)
    pdf.line(detail_left, detail_bottom + detail_total_height, detail_right, detail_bottom + detail_total_height)
    cursor = detail_left
    for cell_width in detail_widths[:-1]:
        cursor += cell_width
        pdf.line(cursor, detail_bottom + detail_total_height, cursor, detail_top)
    pdf.setFont(bold, 6.3)
    for index, title in enumerate(("DIA", "FECHA", "HORAS", "RENDIM.")):
        x = detail_left + sum(detail_widths[:index])
        pdf.drawCentredString(x + detail_widths[index] / 2, detail_top - 4.5 * mm, title)
    total_performance = Decimal("0")
    for index, row in enumerate(daily_rows):
        row_y = detail_top - detail_header - (index + 0.7) * detail_row_height
        day = DAY_NAMES.get(clean(row.get("day")).upper(), clean(row.get("day"))[:2].upper())
        values = (day, display_date(row.get("date")), short_number(row.get("hours")), short_number(row.get("performance")))
        pdf.setFont(regular, 6.3)
        for cell_index, value in enumerate(values):
            x = detail_left + sum(detail_widths[:cell_index])
            if cell_index < 2:
                pdf.drawCentredString(x + detail_widths[cell_index] / 2, row_y, value)
            else:
                pdf.drawRightString(x + detail_widths[cell_index] - 2 * mm, row_y, value)
        total_performance += amount(row.get("performance") or 0)
    pdf.setFont(regular, 6.2)
    pdf.drawCentredString(detail_left + 35 * mm, detail_bottom + 2.4 * mm, "TOTAL DETALLE")
    pdf.setFont(bold, 6.2)
    pdf.drawRightString(detail_right - 2 * mm, detail_bottom + 2.4 * mm, short_number(total_performance))

    signature_left = detail_right + 8 * mm
    signature_right = right - 4 * mm
    signature_center = (signature_left + signature_right) / 2
    line_y = detail_top - 10 * mm
    if signature_path:
        try:
            pdf.drawImage(signature_path, signature_center - 24 * mm, line_y + 1.5 * mm, 48 * mm, 16 * mm, preserveAspectRatio=True, anchor="c", mask="auto")
        except Exception as exc:
            raise PayrollTextError("No se pudo insertar la firma registrada en la boleta.") from exc
    pdf.line(signature_left, line_y, signature_right, line_y)
    pdf.setFont(regular, 7.3)
    pdf.drawCentredString(signature_center, line_y - 5.5 * mm, clean(header.get("apenom"), "TRABAJADOR"))
    pdf.setFont(bold, 7)
    pdf.drawCentredString(signature_center, line_y - 12 * mm, "D.N.I.: {}".format(clean(header.get("documento"), "-")))
    if employer_signature_path:
        try:
            pdf.drawImage(employer_signature_path, signature_center - 24 * mm, detail_bottom + 1 * mm, 48 * mm, 18 * mm, preserveAspectRatio=True, anchor="c", mask="auto")
        except Exception as exc:
            raise PayrollTextError("No se pudo insertar la firma del empleador en la boleta.") from exc

    draw_delivery_footer(pdf, left, right, delivery)

    pdf.showPage()
    pdf.save()
    return output.getvalue()
