"""Lectura estricta de la exportación TXT multisección de Nisira ERG."""
import csv
import re
from pathlib import Path
from decimal import Decimal, InvalidOperation
from datetime import datetime


class PayrollTextError(ValueError):
    pass


def amount(value):
    try:
        result = Decimal(str(value).strip() or '0')
        if not result.is_finite():
            raise InvalidOperation()
        return result
    except InvalidOperation:
        raise PayrollTextError('Importe no válido en el TXT.')


def read_payroll(path, period, document=None):
    path = Path(path)
    if not re.fullmatch(r'\d{6}', period):
        raise PayrollTextError('Período no válido; usa AAAAMM.')
    if period < '202608':
        raise PayrollTextError('Las boletas están disponibles desde agosto de 2026.')
    try:
        datetime.strptime(period, '%Y%m')
    except ValueError:
        raise PayrollTextError('Mes no válido.')
    raw = path.read_bytes()
    if len(raw) > 5 * 1024 * 1024:
        raise PayrollTextError('TXT demasiado grande.')
    try:
        text = raw.decode('utf-8-sig')
    except UnicodeDecodeError:
        text = raw.decode('cp1252')
    rows = list(csv.reader(text.splitlines(), delimiter='|'))
    if len(rows) < 4 or 'documento' not in rows[0] or len(rows[0]) != len(rows[1]):
        raise PayrollTextError('Cabecera TXT incompleta.')
    header = dict(zip(rows[0], (v.strip() for v in rows[1])))
    required = {'codigo', 'documento', 'periodo', 'descripcion_planilla', 'desde1', 'hasta1', 'tot_ingresos', 'tot_descuentos', 'tot_aportes', 'apenom'}
    if not required.issubset(header):
        raise PayrollTextError('Faltan campos obligatorios de cabecera.')
    dni = header['documento']
    if not re.fullmatch(r'\d{8}', dni) or (document and dni != document) or path.stem.split('_')[0] != dni:
        raise PayrollTextError('El DNI del archivo no coincide con su contenido.')
    if header.get('periodo') != period:
        raise PayrollTextError('El TXT corresponde a otro período.')
    if 'GENERAL' not in header.get('descripcion_planilla', '').upper():
        raise PayrollTextError('El TXT no corresponde a régimen general.')
    for key in ('desde1', 'hasta1'):
        try:
            date = datetime.strptime(header[key], '%Y%m%d')
        except (ValueError, KeyError):
            raise PayrollTextError('Fechas no válidas en el TXT.')
        if date.strftime('%Y%m') != period:
            raise PayrollTextError('Las fechas del TXT no corresponden al mes.')
    if header['desde1'] > header['hasta1']:
        raise PayrollTextError('Fechas invertidas en el TXT.')
    try:
        index = next(i for i, row in enumerate(rows) if row[:3] == ['codigo', 'copia', 'item'])
    except StopIteration:
        raise PayrollTextError('Falta la sección de conceptos.')
    fields = rows[index]
    if not {'ingr_valor', 'desc_valor', 'apor_valor', 'tiem_valor'}.issubset(fields):
        raise PayrollTextError('Faltan columnas de conceptos.')
    details = []
    for row in rows[index + 1:]:
        if not row or row[0] == 'codigo':
            break
        if len(row) != len(fields):
            raise PayrollTextError('Fila de conceptos incompleta.')
        detail = dict(zip(fields, (v.strip() for v in row)))
        if detail['codigo'] != header['codigo']:
            raise PayrollTextError('Conceptos de un trabajador distinto.')
        details.append(detail)
    if not details:
        raise PayrollTextError('El TXT no tiene conceptos.')
    # La exportación recibida trae una sola copia lógica; no sumar copias repetidas.
    if len({r['copia'] for r in details}) != 1:
        raise PayrollTextError('El TXT contiene varias copias; requiere revisión para no duplicar importes.')
    if len({r['item'] for r in details}) != len(details):
        raise PayrollTextError('Items duplicados en el TXT.')
    totals = {}
    for field, prefix in [('tot_ingresos', 'ingr'), ('tot_descuentos', 'desc'), ('tot_aportes', 'apor')]:
        total = sum((amount(r[prefix + '_valor']) for r in details), Decimal('0'))
        if total != amount(header[field]):
            raise PayrollTextError('Los conceptos no cuadran con {}.'.format(field))
        totals[prefix] = total
    totals['net'] = totals['ingr'] - totals['desc']
    return {'header': header, 'details': details, 'totals': totals, 'source': str(path)}


def locate_payroll(root, period, document):
    if not re.fullmatch(r'\d{6}', period) or not re.fullmatch(r'\d{8}', document):
        raise PayrollTextError('DNI o período no válido.')
    root = Path(root)
    if not root.is_dir():
        raise PayrollTextError('La carpeta de boletas TXT no está disponible. Verifica la VPN.')
    candidates = set()
    for folder in root.iterdir():
        if folder.is_dir() and folder.name.startswith(period):
            for location in (folder, folder / 'normal'):
                for name in (document + '_N.txt', document + '.txt'):
                    candidate = location / name
                    if candidate.is_file():
                        candidates.add(candidate)
    if len(candidates) != 1:
        raise PayrollTextError('No se encontró un TXT único del trabajador para el mes seleccionado.')
    return next(iter(candidates))
