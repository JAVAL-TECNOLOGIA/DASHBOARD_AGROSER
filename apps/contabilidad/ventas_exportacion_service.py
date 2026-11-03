from collections import defaultdict
from datetime import date
from decimal import Decimal
import json
from pathlib import Path
import re

from django.core.cache import cache
from django.db import connections


MONTHS = [
    'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
    'Julio', 'Agosto', 'Setiembre', 'Octubre', 'Noviembre', 'Diciembre',
]
FIRST_REPORT_YEAR = 2025
CACHE_KEY = 'contabilidad:ventas-exportacion:nisira:v1'
CACHE_SECONDS = 10 * 60
DETAIL_REFERENCE_PATH = Path(__file__).resolve().parent / 'data' / 'ventas_exportacion_detalle.json'


def _number(value):
    if value in (None, ''):
        return 0.0
    return float(value)


def _text(value, default=''):
    return str(value or default).strip()


def _iso_date(value):
    if hasattr(value, 'date'):
        value = value.date()
    return value.isoformat()


def _period_parts(value, fallback_date):
    period = re.sub(r'\D', '', _text(value))
    if len(period) >= 6:
        return int(period[:4]), int(period[4:6]) - 1
    return fallback_date.year, fallback_date.month - 1


def _document_key(value):
    return re.sub(r'[^A-Z0-9]', '', _text(value).upper())


def _document_keys(value):
    text = _text(value).upper()
    keys = {_document_key(text)}
    for series, number in re.findall(r'(F\d{3})\D*0*(\d+)', text):
        keys.add(f'{series}{int(number)}')
    keys.discard('')
    return keys


def _primary_document_key(value):
    matches = re.findall(r'(F\d{3})\D*0*(\d+)', _text(value).upper())
    if matches:
        series, number = matches[-1]
        return f'{series}{int(number)}'
    return _document_key(value)


def _load_invoice_detail_reference():
    try:
        with DETAIL_REFERENCE_PATH.open(encoding='utf-8') as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return {}


def _is_export_purchase(detail, glosa, export_documents):
    text = f'{_text(detail)} {_text(glosa)}'.upper()
    purchase_documents = _document_keys(text)
    compact = _document_key(text)
    if purchase_documents.intersection(export_documents):
        return True
    if any(document and document in compact for document in export_documents):
        return True
    return any(token in text for token in (
        'AWB', 'AGENTE ADUANA', 'HANDLING', 'TRAMITE DOCUMENTARIO AEREO',
        'TRÁMITE DOCUMENTARIO AÉREO', 'SERVICIO DE EXPORTACION',
        'SERVICIO DE EXPORTACIÓN',
    ))


def empty_export_sales_report(current_year=None):
    current_year = current_year or date.today().year
    years = list(range(FIRST_REPORT_YEAR, max(FIRST_REPORT_YEAR, current_year) + 1))
    return {
        'months': MONTHS,
        'years': years,
        'summary': [],
        'invoices': [],
        'purchases': [],
        'customers': [],
        'source': 'NISIRA ERP · Registro de Ventas y Registro de Compras',
    }


def build_export_sales_report(sales_rows, purchase_rows, current_year=None):
    report = empty_export_sales_report(current_year=current_year)
    allowed_years = set(report['years'])
    monthly = defaultdict(lambda: {
        'affected': 0.0,
        'exported': 0.0,
        'exempt': 0.0,
        'sales_tax': 0.0,
        'purchases_base': 0.0,
        'purchases_tax': 0.0,
        'purchases_total': 0.0,
        'purchases_non_taxed': 0.0,
        'export_cost_base': 0.0,
        'export_cost_tax': 0.0,
        'export_cost_total': 0.0,
    })
    export_documents = set()
    invoice_detail_reference = _load_invoice_detail_reference()

    for row in sales_rows:
        sale_date = row['date']
        if not sale_date or sale_date.year not in allowed_years:
            continue
        affected = _number(row.get('affected'))
        exported = _number(row.get('exported'))
        exempt = _number(row.get('exempt'))
        document = _text(row.get('document'))
        if exported or row.get('is_export_credit'):
            reference_key = f'{_iso_date(sale_date)}|{_primary_document_key(document)}'
            detail_values = invoice_detail_reference.get(reference_key, [0, 0, 0])
            export_documents.update(_document_keys(document))
            export_documents.update(_document_keys(row.get('reference')))
            report['invoices'].append({
                'year': sale_date.year,
                'month': sale_date.month - 1,
                'date': _iso_date(sale_date),
                'document_type': _text(row.get('document_type')),
                'document': document,
                'customer': _text(row.get('customer'), 'SIN RAZÓN SOCIAL').upper(),
                'exported': round(exported, 2),
                'currency': _text(row.get('currency')).upper(),
                'exchange_rate': round(_number(row.get('exchange_rate')), 4),
                'total_usd': round(_number(row.get('total_usd')), 2),
                'total_pen': round(_number(row.get('total_pen')), 2),
                'boxes': round(_number(detail_values[0]), 2),
                'price_fob_box': round(_number(detail_values[1]), 4),
                'price_kg_mp': round(_number(detail_values[2]), 4),
                'reference': _text(row.get('reference')),
            })
        key = (sale_date.year, sale_date.month - 1)
        monthly[key]['affected'] += affected
        monthly[key]['exported'] += exported
        monthly[key]['exempt'] += exempt
        monthly[key]['sales_tax'] += _number(row.get('sales_tax'))

    export_documents.discard('')
    for row in purchase_rows:
        purchase_date = row['date']
        if not purchase_date:
            continue
        purchase_year, purchase_month = _period_parts(row.get('period'), purchase_date)
        if purchase_year not in allowed_years:
            continue
        has_nisira_breakdown = 'export_base' in row
        if has_nisira_breakdown:
            export_base = _number(row.get('export_base'))
            export_tax = _number(row.get('export_tax'))
            base = export_base + _number(row.get('general_base'))
            tax = export_tax + _number(row.get('general_tax'))
            non_taxed = _number(row.get('non_taxed'))
        else:
            export_base = 0.0
            export_tax = 0.0
            base = _number(row.get('base'))
            tax = _number(row.get('tax'))
            non_taxed = _number(row.get('total')) - base - tax
        key = (purchase_year, purchase_month)
        monthly[key]['purchases_base'] += base
        monthly[key]['purchases_tax'] += tax
        monthly[key]['purchases_total'] += _number(row.get('total'))
        monthly[key]['purchases_non_taxed'] += non_taxed
        is_export_purchase = bool(export_base or export_tax) or _is_export_purchase(
            row.get('detail'), row.get('glosa'), export_documents,
        )
        if not is_export_purchase:
            continue
        if not has_nisira_breakdown:
            export_base = base
            export_tax = tax
        monthly[key]['export_cost_base'] += export_base
        monthly[key]['export_cost_tax'] += export_tax
        monthly[key]['export_cost_total'] += export_base + export_tax
        report['purchases'].append({
            'year': purchase_year,
            'month': purchase_month,
            'date': _iso_date(purchase_date),
            'document_type': _text(row.get('document_type')),
            'document': _text(row.get('document')),
            'tax_id': _text(row.get('tax_id')),
            'supplier': _text(row.get('supplier'), 'SIN PROVEEDOR').upper(),
            'base': round(base, 2),
            'tax': round(tax, 2),
            'total': round(_number(row.get('total')), 2),
            'currency': _text(row.get('currency')).upper(),
            'exchange_rate': round(_number(row.get('exchange_rate')), 4),
            'detail': _text(row.get('detail') or row.get('glosa')),
        })

    for year in report['years']:
        for month in range(12):
            values = monthly[(year, month)]
            sales_with_export = values['affected'] + values['exported'] + values['exempt']
            sales_without_export = values['affected'] + values['exempt']
            sales_total_with_export = sales_with_export + values['sales_tax']
            sales_total_without_export = sales_without_export + values['sales_tax']
            purchases_without_export = max(
                0.0, values['purchases_base'] - values['export_cost_base']
            )
            purchase_tax_without_export = (
                values['purchases_tax'] - values['export_cost_tax']
            )
            purchases_total_without_export = (
                values['purchases_total'] - values['export_cost_total']
            )
            purchases_non_taxed = values['purchases_non_taxed']
            export_cost_non_taxed = (
                values['export_cost_total']
                - values['export_cost_base']
                - values['export_cost_tax']
            )
            purchases_non_taxed_without_export = (
                purchases_non_taxed - export_cost_non_taxed
            )
            income_tax_with_export = sales_with_export * 0.008
            income_tax_without_export = sales_without_export * 0.008
            drawback = values['exported'] * 0.03
            igv_difference_with_export = values['sales_tax'] - values['purchases_tax']
            igv_difference_without_export = (
                values['sales_tax'] - purchase_tax_without_export
            )
            report['summary'].append({
                'year': year,
                'month': month,
                'sales_with_export': round(sales_with_export, 2),
                'sales_without_export': round(sales_without_export, 2),
                'export_sales': round(values['exported'], 2),
                'export_cost': round(values['export_cost_base'], 2),
                'purchases_with_export': round(values['purchases_base'], 2),
                'purchases_without_export': round(purchases_without_export, 2),
                'affected_sales': round(values['affected'], 2),
                'exempt_sales': round(values['exempt'], 2),
                'sales_total_with_export': round(sales_total_with_export, 2),
                'sales_total_without_export': round(sales_total_without_export, 2),
                'sales_tax': round(values['sales_tax'], 2),
                'purchase_tax': round(values['purchases_tax'], 2),
                'export_purchase_tax': round(values['export_cost_tax'], 2),
                'purchase_tax_without_export': round(purchase_tax_without_export, 2),
                'purchases_total_with_export': round(values['purchases_total'], 2),
                'purchases_total_without_export': round(purchases_total_without_export, 2),
                'purchases_non_taxed': round(purchases_non_taxed, 2),
                'purchases_non_taxed_without_export': round(purchases_non_taxed_without_export, 2),
                'export_cost_non_taxed': round(export_cost_non_taxed, 2),
                'income_tax_with_export': round(income_tax_with_export, 2),
                'income_tax_without_export': round(income_tax_without_export, 2),
                'drawback': round(drawback, 2),
                'igv_difference_with_export': round(igv_difference_with_export, 2),
                'igv_difference_without_export': round(igv_difference_without_export, 2),
                'income_tax_difference': round(
                    income_tax_without_export - income_tax_with_export, 2
                ),
                'igv_scenario_difference': round(
                    igv_difference_without_export - igv_difference_with_export, 2
                ),
                'drawback_difference': round(drawback, 2),
            })

    report['invoices'].sort(key=lambda item: (item['date'], item['document']))
    report['purchases'].sort(key=lambda item: (item['date'], item['document']))
    report['customers'] = sorted({item['customer'] for item in report['invoices']})
    return report


def _dict_rows(cursor):
    columns = [column[0].upper() for column in cursor.description]
    return columns, cursor.fetchall()


def _pick(columns, row, name, default=None):
    try:
        return row[columns.index(name)]
    except ValueError:
        return default


def get_export_sales_report():
    cached = cache.get(CACHE_KEY)
    if cached is not None:
        return cached

    today = date.today()
    sales_rows = []
    purchase_rows = []
    with connections['payroll'].cursor() as cursor:
        cursor.execute(
            'EXEC OBJREPORTES_REGISTROVENTAS %s, %s, %s, %s, %s, %s',
            ['001', f'{FIRST_REPORT_YEAR}01', f'{today.year}12', 'N', '', 0],
        )
        while cursor.description is None and cursor.nextset():
            pass
        columns, rows = _dict_rows(cursor)
        for row in rows:
            exported = _pick(columns, row, 'BASEIMP_EXPO', Decimal('0'))
            document_type = _text(_pick(columns, row, 'IDDOCUMENTO')).upper()
            reference = _pick(columns, row, 'DOC_REFE')
            sales_rows.append({
                'date': _pick(columns, row, 'FECHA'),
                'document_type': _pick(columns, row, 'DSC_DOCUMENTO', document_type),
                'document': _pick(columns, row, 'NUMDOCUMENTO'),
                'customer': _pick(columns, row, 'RAZON_SOCIAL'),
                'affected': _pick(columns, row, 'BASEIMP_AFEC'),
                'exported': exported,
                'exempt': _pick(columns, row, 'BASEIMP_EXON'),
                'sales_tax': _pick(columns, row, 'IMPTO_AFEC'),
                'currency': _pick(columns, row, 'MONEDA'),
                'exchange_rate': _pick(columns, row, 'TCAMBIO'),
                'total_usd': _pick(columns, row, 'TOTALUS'),
                'total_pen': _pick(columns, row, 'TOTAL'),
                'reference': reference,
                'is_export_credit': (
                    document_type in {'NCR', 'NCA', 'NC'}
                    and 'F002' in _document_key(reference)
                ),
            })

        cursor.execute(
            'EXEC CP_REGISTROCOMPRAS_2008 %s, %s, %s, %s, %s',
            # NISIRA usa "N" para expresar todo el registro en moneda nacional.
            # Es la misma variante empleada por el comparativo contable del Excel.
            ['001', f'{FIRST_REPORT_YEAR}01', f'{today.year}12', 'N', 'N'],
        )
        while cursor.description is None and cursor.nextset():
            pass
        columns, rows = _dict_rows(cursor)
        for row in rows:
            export_base = _number(_pick(columns, row, 'AFECTO1'))
            general_base = sum(_number(_pick(columns, row, name)) for name in (
                'AFECTO2', 'AFECTO3',
            ))
            non_taxed = _number(_pick(columns, row, 'AFECTO4'))
            export_tax = _number(_pick(columns, row, 'IMPTO1'))
            general_tax = sum(_number(_pick(columns, row, name)) for name in (
                'IMPTO2', 'IMPTO3', 'IMPTO4',
            ))
            purchase_rows.append({
                'date': _pick(columns, row, 'FECHA'),
                'document_type': _pick(columns, row, 'IDDOCUMENTO'),
                'document': ' '.join(filter(None, [
                    _text(_pick(columns, row, 'SERIE')),
                    _text(_pick(columns, row, 'NUMERO')),
                ])).strip(),
                'tax_id': _pick(columns, row, 'RUC'),
                'supplier': _pick(columns, row, 'RAZON_SOCIAL'),
                'export_base': export_base,
                'general_base': general_base,
                'non_taxed': non_taxed,
                'export_tax': export_tax,
                'general_tax': general_tax,
                'total': _pick(columns, row, 'TOTAL'),
                'currency': _pick(columns, row, 'MONEDA'),
                'exchange_rate': _pick(columns, row, 'TCAMBIO'),
                'detail': _pick(columns, row, 'DETALLE'),
                'glosa': _pick(columns, row, 'GLOSA'),
                'period': _pick(columns, row, 'PERIODO'),
            })

    report = build_export_sales_report(
        sales_rows, purchase_rows, current_year=today.year,
    )
    cache.set(CACHE_KEY, report, CACHE_SECONDS)
    return report
