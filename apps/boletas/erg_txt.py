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


def read_payroll(path, period, document=None, payroll_type='ERG'):
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
    payroll_type = str(payroll_type or 'ERG').strip().upper()
    document_pattern = r'\d{8,12}' if payroll_type in ('OBP', 'OBR') else r'\d{8}'
    dni = header['documento']
    if not re.fullmatch(document_pattern, dni) or (document and dni != document) or path.stem.split('_')[0] != dni:
        raise PayrollTextError('El DNI del archivo no coincide con su contenido.')
    if header.get('periodo') != period:
        raise PayrollTextError('El TXT corresponde a otro período.')
    description = header.get('descripcion_planilla', '').upper()
    if payroll_type == 'ERG' and ('GENERAL' not in description or 'AGRARIO' in description):
        raise PayrollTextError('El TXT no corresponde a régimen general.')
    if payroll_type == 'ERA' and 'AGRARIO' not in description:
        raise PayrollTextError('El TXT no corresponde a régimen agrario.')
    if payroll_type == 'OBP' and (
        'OBREROS PLANTA' not in description or 'GENERAL' in description
    ):
        raise PayrollTextError('El TXT no corresponde a obreros planta.')
    if payroll_type == 'OBR' and 'OBREROS PLANTA GENERAL' not in description:
        raise PayrollTextError('El TXT no corresponde a obreros planta general.')
    if payroll_type not in ('ERG', 'ERA', 'OBP', 'OBR'):
        raise PayrollTextError('Tipo de planilla TXT no válido.')
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

    # Las planillas semanales incluyen dos secciones adicionales: marcación
    # diaria y rendimiento. Se enlazan por posición porque así las exporta Nisira.
    section_headers = [
        row_index for row_index, row in enumerate(rows)
        if row and row[0] == 'codigo'
    ]

    def section_with(field):
        for row_index in section_headers:
            fields = rows[row_index]
            if field not in fields or row_index + 1 >= len(rows):
                continue
            values = rows[row_index + 1]
            if len(values) != len(fields):
                raise PayrollTextError('Fila de detalle diario incompleta.')
            result = dict(zip(fields, (value.strip() for value in values)))
            if result.get('codigo') != header['codigo']:
                raise PayrollTextError('Detalle diario de un trabajador distinto.')
            return result
        return {}

    attendance = section_with('fecha1')
    performance = section_with('rdia1')
    daily_details = []
    if payroll_type in ('OBP', 'OBR'):
        for day_index in range(1, 17):
            raw_date = attendance.get('fecha{}'.format(day_index), '')
            if not raw_date:
                continue
            try:
                datetime.strptime(raw_date, '%Y%m%d')
            except ValueError:
                raise PayrollTextError('Fecha diaria no válida en el TXT.')
            hour_fields = (
                'normales', 'extras125', 'extras135', 'dobles', 'nocturnas',
                'nocextras125', 'nocextras135', 'nocdobles',
            )
            hours = sum(
                (amount(attendance.get('{}{}'.format(field, day_index), 0)) for field in hour_fields),
                Decimal('0'),
            )
            performance_value = amount(performance.get('rdia{}'.format(day_index), 0))
            daily_details.append({
                'day': attendance.get('dia{}'.format(day_index), ''),
                'date': raw_date,
                'hours': hours,
                'performance': performance_value,
            })

    return {
        'header': header,
        'details': details,
        'daily_details': daily_details,
        'totals': totals,
        'source': str(path),
    }


def locate_payroll(root, period, document, week_number=''):
    if not re.fullmatch(r'\d{6}', period) or not re.fullmatch(r'\d{8,12}', document):
        raise PayrollTextError('DNI o período no válido.')
    root = Path(root)
    if not root.is_dir():
        raise PayrollTextError('La carpeta de boletas TXT no está disponible. Verifica la VPN.')
    candidates = set()
    for folder in root.iterdir():
        folder_match = re.fullmatch(r'(\d{6})(\d+)-(\d{6})(\d+)', folder.name)
        matches_period = folder.name.startswith(period)
        if week_number:
            matches_period = bool(folder_match and (
                (folder_match.group(1) == period and folder_match.group(2) == str(week_number))
                or (folder_match.group(3) == period and folder_match.group(4) == str(week_number))
            ))
        if folder.is_dir() and matches_period:
            for location in (folder, folder / 'normal'):
                for name in (document + '_N.txt', document + '_NS.txt', document + '.txt'):
                    candidate = location / name
                    if candidate.is_file():
                        candidates.add(candidate)
    if len(candidates) != 1:
        raise PayrollTextError('No se encontró un TXT único del trabajador para el mes seleccionado.')
    return next(iter(candidates))
