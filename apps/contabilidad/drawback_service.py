from datetime import date
import json
from pathlib import Path
import re

from django.core.cache import cache
from django.db import connections

from apps.contabilidad.ventas_exportacion_service import get_export_sales_report


MONTHS = [
    'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
    'Julio', 'Agosto', 'Setiembre', 'Octubre', 'Noviembre', 'Diciembre',
]
REFERENCE_PATH = Path(__file__).resolve().parent / 'data' / 'drawback_control_reference.json'
CACHE_KEY = 'contabilidad:control-drawback:nisira:v1'
CACHE_SECONDS = 10 * 60


def _text(value, default=''):
    return str(value or default).strip()


def _number(value):
    if value in (None, ''):
        return 0.0
    return float(value)


def _document_key(value):
    match = re.search(r'(F\d{3})\D*0*(\d+)', _text(value).upper())
    if match:
        return '{}{}'.format(match.group(1), int(match.group(2)))
    return re.sub(r'[^A-Z0-9]', '', _text(value).upper())


def _is_credit_note(invoice):
    document_type = _text(invoice.get('document_type')).upper()
    return 'CREDITO' in document_type or 'CRÉDITO' in document_type or document_type in {
        'NC', 'NCR', 'NCA',
    }


def _load_reference():
    try:
        with REFERENCE_PATH.open(encoding='utf-8') as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return {}


def empty_drawback_report(current_year=None):
    current_year = current_year or date.today().year
    return {
        'months': MONTHS,
        'years': list(range(2025, max(2025, current_year) + 1)),
        'rows': [],
        'customers': [],
        'statuses': ['ABONADA', 'POR SOLICITAR'],
        'transports': ['AEREO', 'MARITIMO'],
        'source': 'NISIRA ERP · Registro de Ventas y Cuentas por Cobrar',
    }


def build_drawback_report(invoices, transport_by_document=None, current_year=None):
    report = empty_drawback_report(current_year=current_year)
    references = _load_reference()
    transport_by_document = transport_by_document or {}
    credits = [invoice for invoice in invoices if _is_credit_note(invoice)]

    for invoice in invoices:
        if _is_credit_note(invoice):
            continue
        invoice_amount = abs(_number(invoice.get('total_usd')))
        if not invoice_amount:
            continue
        document_key = _document_key(invoice.get('document'))
        related_credits = [
            credit for credit in credits
            if _document_key(credit.get('reference')) == document_key
        ]
        adjustment = -sum(abs(_number(credit.get('total_usd'))) for credit in related_credits)
        credit_note = ' / '.join(
            '{} - {}'.format(
                _text(credit.get('document')),
                _text(credit.get('date')),
            ) for credit in related_credits
        )
        reference = references.get(document_key, {})
        exchange_rate = _number(reference.get('payment_exchange_rate')) or _number(
            invoice.get('exchange_rate')
        )
        net_amount = invoice_amount + adjustment
        drawback_usd = net_amount * 0.03
        year = int(invoice['year'])
        month = int(invoice['month'])
        transport = _text(
            transport_by_document.get(document_key)
            or reference.get('transport'),
            'SIN DEFINIR',
        ).upper()
        report['rows'].append({
            'year': year,
            'month': month,
            'date': _text(invoice.get('date')),
            'crop': _text(reference.get('crop'), 'ESPARRAGO').upper(),
            'document': _text(invoice.get('document')),
            'customer': _text(invoice.get('customer'), 'SIN RAZÓN SOCIAL').upper(),
            'transport': transport,
            'invoice_amount': round(invoice_amount, 2),
            'adjustment': round(adjustment, 2),
            'credit_note': credit_note,
            'drawback_usd': round(drawback_usd, 2),
            'payment_exchange_rate': round(exchange_rate, 4),
            'drawback_pen': round(drawback_usd * exchange_rate, 2),
            'status': _text(reference.get('status'), 'POR SOLICITAR').upper(),
        })

    report['rows'].sort(key=lambda item: (item['date'], item['document']))
    report['customers'] = sorted({item['customer'] for item in report['rows']})
    report['statuses'] = sorted({item['status'] for item in report['rows']})
    report['transports'] = sorted({item['transport'] for item in report['rows']})
    return report


def _transport_metadata():
    mapping = {}
    with connections['payroll'].cursor() as cursor:
        cursor.execute(
            '''
            SELECT RTRIM(SERIE), RTRIM(NUMERO), RTRIM(IDVIA_EMBARQUE)
            FROM COBRARPAGARDOC WITH (NOLOCK)
            WHERE IDEMPRESA = %s
              AND YEAR(FECHA) >= 2025
              AND IDDOCUMENTO = 'FAC'
              AND (ISNULL(EXPORTACION, 0) = 1 OR IDESTADO = 'W1')
            ''',
            ['001'],
        )
        transport_names = {'001': 'AEREO', '002': 'MARITIMO'}
        for series, number, transport_id in cursor.fetchall():
            key = _document_key('{}-{}'.format(_text(series), _text(number)))
            mapping[key] = transport_names.get(_text(transport_id), _text(transport_id))
    return mapping


def get_drawback_report():
    cached = cache.get(CACHE_KEY)
    if cached is not None:
        return cached
    export_report = get_export_sales_report()
    report = build_drawback_report(
        export_report['invoices'],
        transport_by_document=_transport_metadata(),
        current_year=date.today().year,
    )
    cache.set(CACHE_KEY, report, CACHE_SECONDS)
    return report
