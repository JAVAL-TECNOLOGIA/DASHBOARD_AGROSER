"""Formato A4 de boleta para empleados de régimen general y agrario."""
from datetime import datetime
from io import BytesIO
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from .erg_txt import PayrollTextError, amount
from .electronic_delivery_pdf import draw_delivery_footer


def build_pdf(data, signature_path=None, employer_signature_path=None, delivery=None):
    header, details, totals = data["header"], data["details"], data["totals"]
    output = BytesIO()
    width, height = A4
    pdf = canvas.Canvas(output, pagesize=A4)
    pdf.setTitle("Boleta de remuneraciones {} {}".format(
        header.get("documento", ""), header.get("periodo", "")
    ))
    pdf.setAuthor(header.get("razon_social", "AGROSERVICE ICA SUR S.A.C."))

    regular, bold = "Helvetica", "Helvetica-Bold"
    fonts = Path("C:/Windows/Fonts")
    if (fonts / "arial.ttf").is_file() and (fonts / "arialbd.ttf").is_file():
        if "Employee-Arial" not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont("Employee-Arial", str(fonts / "arial.ttf")))
            pdfmetrics.registerFont(TTFont("Employee-Arial-Bold", str(fonts / "arialbd.ttf")))
        regular, bold = "Employee-Arial", "Employee-Arial-Bold"

    left, right = 2.5 * mm, width - 2.5 * mm
    content_width = right - left

    def clean(value, default=""):
        return str(value).strip() if value not in (None, "") else default

    def money(value):
        return "{:,.2f}".format(amount(value or 0))

    def display_date(value, empty=" / /"):
        raw = clean(value)
        if not raw:
            return empty
        for pattern in ("%Y%m%d", "%Y-%m-%d", "%d/%m/%Y"):
            try:
                return datetime.strptime(raw[:10], pattern).strftime("%d/%m/%Y")
            except ValueError:
                continue
        return raw

    def fit(value, available, font=regular, size=7):
        original = clean(value, "-")
        fitted = original
        while len(fitted) > 1 and pdf.stringWidth(fitted, font, size) > available:
            fitted = fitted[:-1]
        return fitted if fitted == original else fitted.rstrip() + "..."

    def label_value(label, value, x, y, label_width, value_width, strong=False, size=7.2):
        pdf.setFont(bold, size)
        pdf.drawString(x, y, label)
        pdf.setFont(bold if strong else regular, size)
        pdf.drawString(x + label_width, y, fit(value, value_width, bold if strong else regular, size))

    top = height - 18 * mm
    pdf.setFont(regular, 8)
    pdf.drawString(left, top, clean(header.get("razon_social"), "AGROSERVICE ICA SUR S.A.C."))
    pdf.setFont(regular, 7.3)
    pdf.drawString(left, top - 5.2 * mm, "R.U.C : {}".format(clean(header.get("ruc"), "20534627077")))
    pdf.drawString(left, top - 10.5 * mm, fit(header.get("direccion_empresa"), content_width, regular, 7.3))

    pdf.setFont(bold, 11.2)
    pdf.drawCentredString(width / 2, height - 39 * mm, "BOLETA DE REMUNERACIONES")

    info_top = height - 49 * mm
    info_right = left + 139 * mm
    right_value = info_right + 31 * mm
    employee_code = clean(header.get("codigo") or header.get("documento"), "-")
    employee_name = clean(header.get("apenom"), "-")
    affiliate = "{} - {}".format(clean(header.get("afp")), clean(header.get("afp_dsc"))).strip(" -")
    cussp = "{} {}".format(clean(header.get("autogene")), clean(header.get("autoipss"))).strip()

    label_value("CODIGO :", "{}  {}".format(employee_code, employee_name), left, info_top, 24 * mm, 112 * mm, strong=True)
    label_value("SUELDO :", "{}   {}".format(clean(header.get("moneda"), "S/"), money(header.get("basico"))), info_right, info_top, 31 * mm, right - right_value, strong=True)
    label_value("CARGO :", header.get("cargo"), left, info_top - 6 * mm, 24 * mm, 112 * mm)
    label_value("DNI", header.get("documento"), info_right, info_top - 6 * mm, 31 * mm, right - right_value)
    label_value("AFP :", affiliate, left, info_top - 12 * mm, 24 * mm, 56 * mm)
    label_value("CUSSP/ONP :", cussp, left + 82 * mm, info_top - 12 * mm, 30 * mm, 25 * mm)
    label_value("FEC. INGRESO", display_date(header.get("ingreso"), "-"), info_right, info_top - 12 * mm, 31 * mm, right - right_value)
    label_value("SITUACION :", clean(header.get("situacion_especial"), "NINGUNO"), left, info_top - 18 * mm, 31 * mm, 105 * mm)
    label_value("FEC. CESE :", display_date(header.get("cese")), info_right, info_top - 18 * mm, 31 * mm, right - right_value)

    period_top = height - 68 * mm
    period_height = 8.5 * mm
    pdf.setLineWidth(0.5)
    pdf.rect(left, period_top - period_height, content_width, period_height)
    pdf.setFont(regular, 7.5)
    pdf.drawString(left + 1 * mm, period_top - 5.5 * mm, "PERIODO {} DEL {} AL {}".format(
        clean(header.get("periodo"), "-"),
        display_date(header.get("desde1"), "-"),
        display_date(header.get("hasta1"), "-"),
    ))

    table_top = period_top - period_height
    table_bottom = 104 * mm
    header_height = 13 * mm
    column_width = content_width / 4
    headings = (
        (("REMUNERACIONES",), "ingr"),
        (("RETENCIONES AL", "TRABAJADOR"), "desc"),
        (("CONTRIBUCIONES", "DEL EMPLEADOR"), "apor"),
        (("TIEMPOS",), "tiem"),
    )
    pdf.rect(left, table_bottom, content_width, table_top - table_bottom)
    pdf.line(left, table_top - header_height, right, table_top - header_height)
    for index, (heading_lines, prefix) in enumerate(headings):
        x = left + index * column_width
        if index:
            pdf.line(x, table_bottom, x, table_top)
        pdf.setFont(regular, 6.8)
        first_y = table_top - (5.6 if len(heading_lines) == 1 else 4.2) * mm
        for line_index, heading in enumerate(heading_lines):
            pdf.drawCentredString(x + column_width / 2, first_y - line_index * 4.1 * mm, heading)
        concept_rows = [
            (clean(row.get(prefix + "_descri")), row.get(prefix + "_valor"))
            for row in details if clean(row.get(prefix + "_descri"))
        ]
        if len(concept_rows) > 20:
            raise PayrollTextError("Los conceptos exceden el espacio del formato de boleta.")
        font_size = 6.1 if len(concept_rows) <= 15 else 5.2
        row_step = 5.2 * mm if len(concept_rows) <= 15 else 4.1 * mm
        row_y = table_top - header_height - 5.5 * mm
        for description, value in concept_rows:
            pdf.setFont(regular, font_size)
            pdf.drawString(x + 1 * mm, row_y, fit(description, column_width - 18 * mm, regular, font_size))
            pdf.drawRightString(x + column_width - 1.2 * mm, row_y, money(value))
            row_y -= row_step

    totals_top = table_bottom
    totals_bottom = 80 * mm
    pdf.rect(left, totals_bottom, content_width, totals_top - totals_bottom)
    for index in range(1, 4):
        pdf.line(left + index * column_width, totals_bottom, left + index * column_width, totals_top)
    total_rows = (
        ("TOTAL INGRESOS", totals["ingr"]),
        ("TOTAL RETENCIONES S/.", totals["desc"]),
        ("TOTAL APORTACION S/.", totals["apor"]),
        ("NETO A PAGAR S/.", totals["net"]),
    )
    for index, (label, value) in enumerate(total_rows):
        x = left + index * column_width
        pdf.setFont(bold if index == 3 else regular, 9 if index == 3 else 7.1)
        pdf.drawString(x + 1.2 * mm, totals_top - 5.5 * mm, label)
        pdf.setFont(bold if index == 3 else regular, 10.5 if index == 3 else 8.8)
        pdf.drawRightString(x + column_width - 5 * mm, totals_bottom + 10.5 * mm, money(value))

    employer_x = left + 24 * mm
    if employer_signature_path:
        try:
            pdf.drawImage(employer_signature_path, employer_x, 41 * mm, 48 * mm, 18 * mm, preserveAspectRatio=True, anchor="c", mask="auto")
        except Exception as exc:
            raise PayrollTextError("No se pudo insertar la firma del empleador en la boleta.") from exc

    worker_left, worker_right = width - 67 * mm, width - 18 * mm
    worker_center = (worker_left + worker_right) / 2
    worker_line_y = 43 * mm
    if signature_path:
        try:
            pdf.drawImage(signature_path, worker_center - 23 * mm, worker_line_y + 1.5 * mm, 46 * mm, 17 * mm, preserveAspectRatio=True, anchor="c", mask="auto")
        except Exception as exc:
            raise PayrollTextError("No se pudo insertar la firma registrada en la boleta.") from exc
    pdf.line(worker_left, worker_line_y, worker_right, worker_line_y)
    pdf.setFont(regular, 8.2)
    pdf.drawCentredString(worker_center, 36.5 * mm, "TRABAJADOR")

    draw_delivery_footer(pdf, left, right, delivery)

    pdf.showPage()
    pdf.save()
    return output.getvalue()
