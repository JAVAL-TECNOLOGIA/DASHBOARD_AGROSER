"""Reconstrucción de las dos copias del reporte rpt_boleta_pago FRX/FRT."""
from io import BytesIO
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Table, TableStyle
from .erg_txt import amount, PayrollTextError


def build_pdf(data, signature_path=None, employer_signature_path=None):
    regular, bold = 'Times-Roman', 'Times-Bold'
    fonts = Path('C:/Windows/Fonts')
    if (fonts / 'gara.ttf').exists() and (fonts / 'garabd.ttf').exists():
        if 'ERG-Garamond' not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont('ERG-Garamond', str(fonts / 'gara.ttf')))
            pdfmetrics.registerFont(TTFont('ERG-Garamond-Bold', str(fonts / 'garabd.ttf')))
        regular, bold = 'ERG-Garamond', 'ERG-Garamond-Bold'
    h, details, totals = data['header'], data['details'], data['totals']
    out = BytesIO()
    width, height = A4[1] / 2, A4[0]
    pdf = canvas.Canvas(out, pagesize=(width, height))
    pdf.setTitle('Boleta ERG {} {}'.format(h['documento'], h['periodo']))
    pdf.setAuthor(h.get('razon_social', 'Agroservice'))
    style = ParagraphStyle('body', fontName=regular, fontSize=7, leading=8)
    def para(value, size=7, strong=False):
        st = ParagraphStyle('cell', parent=style, fontName=bold if strong else regular, fontSize=size, leading=size+1)
        return Paragraph(escape(str(value or '')), st)
    def money(value):
        return '{:,.2f}'.format(amount(value))
    def date(value):
        return '{}/{}/{}'.format(value[6:8], value[4:6], value[:4])
    half = width
    for copy in range(1):
        x, w = copy * half + 6 * mm, half - 12 * mm
        y = height - 10 * mm
        pdf.setFont(bold, 10)
        pdf.drawString(x, y, h.get('razon_social', ''))
        pdf.setFont(regular, 8)
        pdf.drawString(x, y - 4 * mm, 'R.U.C.: ' + h.get('ruc', ''))
        p = para(h.get('direccion_empresa'), 7)
        _, ph = p.wrap(w, 12 * mm); p.drawOn(pdf, x, y - 7 * mm - ph)
        pdf.setFont(bold, 11)
        pdf.drawCentredString(x + w/2, height - 29 * mm, 'BOLETA DE REMUNERACIONES')
        info = [
            [para('CÓDIGO: ' + h['codigo'] + '  ' + h['apenom'], 8, True)],
            [para('DNI: ' + h['documento'] + '    CARGO: ' + h.get('cargo', ''), 8)],
            [para('SUELDO: ' + h.get('moneda', 'S/.') + ' ' + money(h.get('basico', 0)) + '    FEC. INGRESO: ' + h.get('ingreso', ''), 8)],
            [para('AFP: ' + h.get('afp', '') + ' - ' + h.get('afp_dsc', '') + '    CUSSP/ONP: ' + h.get('autogene', '') + ' ' + h.get('autoipss', ''), 8)],
            [para('SITUACIÓN: ' + h.get('situacion_especial', '') + '    FEC. CESE: ' + h.get('cese', ''), 8)],
            [para('PERÍODO: ' + h['periodo'] + '    DEL ' + date(h['desde1']) + ' AL ' + date(h['hasta1']), 8, True)],
        ]
        table = Table(info, colWidths=[w]); table.setStyle(TableStyle([('LEFTPADDING',(0,0),(-1,-1),0),('TOPPADDING',(0,0),(-1,-1),2),('BOTTOMPADDING',(0,0),(-1,-1),2)]))
        _, ih = table.wrap(w, height); top = height - 34 * mm; table.drawOn(pdf,x,top-ih)
        cells = [[para(label,7,True) for label in ('REMUNERACIONES','RETENCIONES AL TRABAJADOR','CONTRIBUCIONES DEL EMPLEADOR','TIEMPOS')]]
        for row in details:
            cols=[]
            for prefix in ('ingr','desc','apor','tiem'):
                label=row.get(prefix+'_descri','')
                if label:
                    nested=Table([[para(label,7),para(money(row[prefix+'_valor']),7)]],colWidths=[w/4-14*mm,12*mm])
                    nested.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),0),('TOPPADDING',(0,0),(-1,-1),1),('BOTTOMPADDING',(0,0),(-1,-1),1)]))
                    cols.append(nested)
                else: cols.append('')
            cells.append(cols)
        concepts=Table(cells,colWidths=[w/4]*4)
        concepts.setStyle(TableStyle([('BOX',(0,0),(-1,-1),.5,'black'),('INNERGRID',(0,0),(-1,0),.5,'black'),('LINEBEFORE',(1,0),(-1,-1),.4,'black'),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),2),('RIGHTPADDING',(0,0),(-1,-1),2),('TOPPADDING',(0,0),(-1,-1),3),('BOTTOMPADDING',(0,0),(-1,-1),3)]))
        _, ch=concepts.wrap(w,height); cy=top-ih-4*mm-ch
        if cy < 53*mm:
            raise PayrollTextError('Los conceptos exceden el espacio del formato; se requiere una página adicional.')
        concepts.drawOn(pdf,x,cy)
        y=cy-6*mm
        for label,value in [('Total ingresos S/.',totals['ingr']),('Total retenciones S/.',totals['desc']),('Total aportaciones S/.',totals['apor']),('NETO A PAGAR S/.',totals['net'])]:
            pdf.setFont(bold if label.startswith('NETO') else regular,9)
            pdf.drawString(x,y,label);pdf.drawRightString(x+w,y,money(value));y-=5*mm
        pdf.line(x+5*mm,18*mm,x+57*mm,18*mm);pdf.line(x+w-57*mm,18*mm,x+w-5*mm,18*mm)
        if employer_signature_path:
            try:
                pdf.drawImage(
                    employer_signature_path,
                    x+10*mm,
                    19*mm,
                    42*mm,
                    14*mm,
                    preserveAspectRatio=True,
                    anchor='c',
                    mask='auto',
                )
            except Exception as exc:
                raise PayrollTextError('No se pudo insertar la firma del empleador en la boleta.') from exc
        if signature_path:
            try:
                pdf.drawImage(
                    signature_path,
                    x+w-52*mm,
                    19*mm,
                    42*mm,
                    14*mm,
                    preserveAspectRatio=True,
                    anchor='c',
                    mask='auto',
                )
            except Exception as exc:
                raise PayrollTextError('No se pudo insertar la firma registrada en la boleta.') from exc
        pdf.setFont(regular,8);pdf.drawCentredString(x+31*mm,14*mm,'EMPLEADOR');pdf.drawCentredString(x+w-31*mm,14*mm,'TRABAJADOR')
        pdf.setFont(regular,7);pdf.drawCentredString(x+w/2,7*mm,'COPIA DEL TRABAJADOR' if copy == 0 else 'CARGO - EMPLEADOR')
    pdf.save()
    return out.getvalue()
