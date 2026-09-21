"""Fotocheck con código de barras Code 128 del documento más el sufijo 1."""
from io import BytesIO
from xml.sax.saxutils import escape
from PIL import Image, ImageOps
from reportlab.graphics.barcode import createBarcodeDrawing
from reportlab.graphics import renderPDF
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.pdfgen import canvas
from .documents import valid_worker_document


BADGE_WIDTH = 86 * mm
BADGE_HEIGHT = 54 * mm


def draw_worker_badge(pdf, document, name, position, photo_file, x=0, y=0):
    if not valid_worker_document(document):
        raise ValueError('El documento debe tener 8 o 9 dígitos.')
    pdf.setFillColor(colors.white)
    pdf.rect(x, y, BADGE_WIDTH, BADGE_HEIGHT, fill=1, stroke=0)
    pdf.setFillColor(colors.HexColor('#12645d'))
    pdf.setFont('Helvetica-Bold', 10)
    pdf.drawString(x + 4 * mm, y + 47 * mm, 'AGROSERVICE ICA SUR')
    pdf.setFillColor(colors.HexColor('#263238'))
    pdf.setFont('Helvetica', 6)
    pdf.drawString(x + 4 * mm, y + 43 * mm, 'FOTOCHECK DEL TRABAJADOR')
    with Image.open(photo_file) as source:
        image = ImageOps.fit(ImageOps.exif_transpose(source).convert('RGB'), (440, 600))
        pdf.drawImage(ImageReader(image), x + 4 * mm, y + 10 * mm, 22 * mm, 30 * mm)
    def paragraph(text, top, size, max_height):
        for font_size in (size, size - 1, size - 2):
            style = ParagraphStyle('badge', fontName='Helvetica-Bold' if size == 8 else 'Helvetica',
                fontSize=font_size, leading=font_size + 1, textColor=colors.HexColor('#263238'))
            p = Paragraph(escape(str(text or 'No registrado')), style)
            _, h = p.wrap(51 * mm, max_height * mm)
            if h <= max_height * mm:
                p.drawOn(pdf, x + 30 * mm, y + top * mm - h)
                return
        raise ValueError('El nombre o cargo es demasiado largo para el fotocheck.')
    paragraph(name, 40, 8, 11)
    paragraph(position, 28, 7, 6)
    pdf.setFont('Helvetica-Bold', 8)
    pdf.drawString(x + 30 * mm, y + 17 * mm, 'Documento: ' + document)
    barcode_value = document + '1'
    barcode = createBarcodeDrawing(
        'Code128', value=barcode_value, barWidth=0.36 * mm,
        barHeight=10 * mm, humanReadable=False,
    )
    renderPDF.draw(barcode, pdf, x + 30 * mm + (51 * mm - barcode.width) / 2, y + 5 * mm)
    pdf.setFont('Helvetica', 5.5)
    pdf.drawCentredString(x + 55.5 * mm, y + 2 * mm, barcode_value)
    pdf.setFont('Helvetica', 5.5)
    pdf.drawString(x + 4 * mm, y + 4 * mm, 'AGROSERVICE · ICA SUR')


def build_worker_badge(document, name, position, photo_file):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=(BADGE_WIDTH, BADGE_HEIGHT))
    pdf.setTitle('Fotocheck - ' + document)
    draw_worker_badge(pdf, document, name, position, photo_file)
    pdf.save()
    return buffer.getvalue()


def build_worker_badge_sheet(workers):
    """Genera seis fotochecks por A4: dos columnas por tres filas."""
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    pdf.setTitle('Fotochecks de trabajadores registrados')
    x_positions = (14 * mm, 110 * mm)
    y_positions = (185.5 * mm, 121.5 * mm, 57.5 * mm)

    for index, worker in enumerate(workers):
        if index and index % 6 == 0:
            pdf.showPage()
        slot = index % 6
        x = x_positions[slot % 2]
        y = y_positions[slot // 2]
        draw_worker_badge(
            pdf,
            worker['document'],
            worker.get('name'),
            worker.get('position'),
            worker['photo'],
            x=x,
            y=y,
        )
        pdf.setStrokeColor(colors.HexColor('#b0bec5'))
        pdf.setLineWidth(0.3)
        pdf.rect(x, y, BADGE_WIDTH, BADGE_HEIGHT, fill=0, stroke=1)

    pdf.save()
    return buffer.getvalue()
