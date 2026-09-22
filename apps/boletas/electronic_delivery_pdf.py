"""Constancias verificables de entrega electrónica para boletas A4."""
from reportlab.lib import colors
from reportlab.lib.units import mm


def draw_delivery_footer(pdf, left, right, delivery):
    """Dibuja un pie de 23 mm; deja intacto el contenido sobre y=26 mm."""
    delivery = delivery or {}
    bottom, height = 2 * mm, 22 * mm
    badge_width = 39 * mm
    note_width = 52 * mm
    details_left = left + badge_width + 2 * mm
    details_right = right - note_width - 2 * mm
    green = colors.HexColor("#08794c")
    border = colors.HexColor("#c6e4d5")

    pdf.setFillColor(green)
    pdf.roundRect(left, bottom, badge_width, height, 2 * mm, fill=1, stroke=0)
    pdf.setFillColor(colors.white)
    pdf.setFont("Helvetica-Bold", 8)
    pdf.drawCentredString(left + badge_width / 2, bottom + 12 * mm, "ENTREGA")
    pdf.drawCentredString(left + badge_width / 2, bottom + 7 * mm, "ELECTRÓNICA")

    rows = (
        ("Medio:", "Portal del trabajador"),
        ("Fecha de emisión:", delivery.get("issued_at") or "No registrada"),
        ("Fecha de puesta a disposición:", delivery.get("released_at") or "No registrada"),
        ("Constancia de emisión:", "Sí (publicación registrada)" if delivery.get("released_at") else "No registrada"),
        ("Constancia de recepción/acceso:", "Sí (acceso registrado)" if delivery.get("accessed_at") else "No registrada"),
    )
    row_height = height / len(rows)
    label_width = 52 * mm
    pdf.setStrokeColor(border)
    pdf.setLineWidth(.35)
    pdf.roundRect(details_left, bottom, details_right - details_left, height, 1.5 * mm, fill=0, stroke=1)
    pdf.line(details_left + label_width, bottom, details_left + label_width, bottom + height)
    for index, (label, value) in enumerate(rows):
        row_bottom = bottom + height - (index + 1) * row_height
        if index:
            pdf.line(details_left, row_bottom + row_height, details_right, row_bottom + row_height)
        pdf.setFillColor(colors.HexColor("#263b31"))
        pdf.setFont("Helvetica-Bold", 5.7)
        pdf.drawString(details_left + 1 * mm, row_bottom + 1.5 * mm, label)
        pdf.setFont("Helvetica", 5.7)
        pdf.drawString(details_left + label_width + 1 * mm, row_bottom + 1.5 * mm, value)

    note_left = details_right + 2 * mm
    pdf.setFillColor(colors.HexColor("#eef9f2"))
    pdf.setStrokeColor(border)
    pdf.roundRect(note_left, bottom, right - note_left, height, 2 * mm, fill=1, stroke=1)
    pdf.setFillColor(green)
    pdf.circle(note_left + 5 * mm, bottom + height - 6 * mm, 2.7 * mm, fill=1, stroke=0)
    pdf.setFillColor(colors.white)
    pdf.setFont("Helvetica-Bold", 6)
    pdf.drawCentredString(note_left + 5 * mm, bottom + height - 6.7 * mm, "i")
    pdf.setFillColor(colors.HexColor("#263b31"))
    pdf.setFont("Helvetica", 5.8)
    for index, line in enumerate((
        "Registro de entrega por",
        "el portal del trabajador.",
        "Referencia: D.S. 001-98-TR",
        "y D.S. 009-2011-TR.",
    )):
        pdf.drawString(note_left + 10 * mm, bottom + height - (5.5 + index * 4) * mm, line)
