"""Pie de entrega electrónica para boletas A4."""
from reportlab.graphics import renderPDF
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing
from reportlab.lib import colors
from reportlab.lib.units import mm


def draw_delivery_footer(pdf, left, right, delivery, qr_data=""):
    delivery = delivery or {}
    bottom, height = 3 * mm, 29 * mm
    badge_width, qr_width, note_width, gap = 39 * mm, 22 * mm, 44 * mm, 1.5 * mm
    details_left = left + badge_width + gap
    note_left = right - note_width
    qr_left = note_left - gap - qr_width
    details_right = qr_left - gap
    green = colors.HexColor("#086f48")
    border = colors.HexColor("#c6dfd5")
    ink = colors.HexColor("#172833")

    pdf.setFillColor(green)
    pdf.roundRect(left, bottom, badge_width, height, 1.5 * mm, fill=1, stroke=0)
    pdf.setFillColor(colors.white)
    pdf.setFont("Helvetica-Bold", 8)
    pdf.drawCentredString(left + badge_width / 2, bottom + 17 * mm, "ENTREGA")
    pdf.drawCentredString(left + badge_width / 2, bottom + 12.5 * mm, "ELECTRÓNICA")
    pdf.setFont("Helvetica", 5.6)
    pdf.drawCentredString(left + badge_width / 2, bottom + 6 * mm, "Portal del trabajador")

    pdf.setFillColor(colors.HexColor("#f4faf7"))
    pdf.setStrokeColor(border)
    pdf.roundRect(details_left, bottom, details_right - details_left, height, 1.5 * mm, fill=1, stroke=1)
    rows = (
        ("Medio:", "Portal del trabajador"),
        ("Fecha de emisión:", delivery.get("issued_at") or "No registrada"),
        ("Fecha de puesta a disposición:", delivery.get("released_at") or "Pendiente"),
        ("Constancia de emisión:", "Sí (autorización registrada)" if delivery.get("issued_at") else "No registrada"),
        ("Constancia de recepción:", "Sí (confirmación registrada)" if delivery.get("accessed_at") else "Pendiente"),
    )
    label_width = 42 * mm
    row_height = height / len(rows)
    pdf.line(details_left + label_width, bottom, details_left + label_width, bottom + height)
    for index, (label, value) in enumerate(rows):
        y = bottom + height - (index + 1) * row_height
        if index:
            pdf.line(details_left, y + row_height, details_right, y + row_height)
        pdf.setFillColor(ink)
        pdf.setFont("Helvetica-Bold", 5.3)
        pdf.drawString(details_left + 1 * mm, y + 2 * mm, label)
        pdf.setFont("Helvetica", 5.3)
        pdf.drawString(details_left + label_width + 1 * mm, y + 2 * mm, value)

    pdf.setFillColor(colors.white)
    pdf.setStrokeColor(border)
    pdf.roundRect(qr_left, bottom, qr_width, height, 1.5 * mm, fill=1, stroke=1)
    if qr_data:
        qr = QrCodeWidget(qr_data)
        x1, y1, x2, y2 = qr.getBounds()
        side = 19 * mm
        drawing = Drawing(side, side, transform=[side / (x2 - x1), 0, 0, side / (y2 - y1), 0, 0])
        drawing.add(qr)
        renderPDF.draw(drawing, pdf, qr_left + 1.5 * mm, bottom + 5.5 * mm)
    pdf.setFillColor(ink)
    pdf.setFont("Helvetica", 5)
    pdf.drawCentredString(qr_left + qr_width / 2, bottom + 2.3 * mm, "Datos de boleta")

    pdf.setFillColor(colors.HexColor("#f4faf7"))
    pdf.setStrokeColor(border)
    pdf.roundRect(note_left, bottom, note_width, height, 1.5 * mm, fill=1, stroke=1)
    pdf.setFillColor(green)
    pdf.circle(note_left + 4 * mm, bottom + height - 5.5 * mm, 2.1 * mm, fill=1, stroke=0)
    pdf.setFillColor(colors.white)
    pdf.setFont("Helvetica-Bold", 5.8)
    pdf.drawCentredString(note_left + 4 * mm, bottom + height - 6.2 * mm, "i")
    pdf.setFillColor(ink)
    pdf.setFont("Helvetica-Bold", 6.1)
    pdf.drawString(note_left + 8 * mm, bottom + height - 6.4 * mm, "Boleta generada")
    pdf.setFont("Helvetica", 5.8)
    for index, line in enumerate((
        "Entrega por el portal",
        "del trabajador.",
        "Referencia: D.S. 001-98-TR",
        "y D.S. 009-2011-TR.",
    )):
        pdf.drawString(note_left + 4 * mm, bottom + height - (11 + index * 4) * mm, line)
