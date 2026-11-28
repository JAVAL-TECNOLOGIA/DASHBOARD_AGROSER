import json
from datetime import date, datetime, time
from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.test import RequestFactory, SimpleTestCase

from . import views
from .nisira_sync import _fetch_procedure_rows, _xml_for_marks


class FakeCursor:
    def __init__(self):
        self.executions = []

    def execute(self, query, params=None):
        self.executions.append((query, params or []))

    def fetchone(self):
        return (time(8, 0), None, date(2026, 11, 27), '12345678', 'ANA', 'PRUEBA')

    def close(self):
        pass


class FakeProcedureCursor:
    def __init__(self):
        self.description = None

    def nextset(self):
        self.description = [('SERIE',), ('NUMERO',)]
        return True

    def fetchall(self):
        return [('0001', '0002997')]


class AttendanceEditingTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_non_admin_cannot_edit_attendance(self):
        request = self.factory.post(
            '/marcadores/api/asistencias/editar/',
            data=json.dumps({'id_asistencia': 1}),
            content_type='application/json',
        )
        request.user = SimpleNamespace(
            is_authenticated=True, is_superuser=False, is_staff=False,
            admin=False, username='WORKER',
        )

        response = views.editar_asistencia(request)

        self.assertEqual(response.status_code, 403)

    def test_admin_edit_creates_audit_log(self):
        request = self.factory.post(
            '/marcadores/api/asistencias/editar/',
            data=json.dumps({
                'id_asistencia': 15,
                'hora_ingreso': '08:10',
                'motivo': 'Corrección de hora de ingreso',
            }),
            content_type='application/json',
        )
        request.user = SimpleNamespace(
            is_authenticated=True, is_superuser=False, is_staff=True,
            admin=True, username='JALCANTARA',
        )
        cursor = FakeCursor()
        connection = Mock()

        with patch.object(views, '_get_portalaei_cursor', return_value=cursor), patch.object(
            views, 'connection_portalaei', connection
        ):
            response = views.editar_asistencia(request)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(any('UPDATE ASISTENCIA' in query for query, _ in cursor.executions))
        self.assertTrue(any('ASISTENCIA_MODIFICACION_LOG' in query and 'INSERT INTO' in query for query, _ in cursor.executions))
        update_params = next(
            params for query, params in cursor.executions if 'UPDATE ASISTENCIA' in query
        )
        self.assertEqual(update_params, [time(8, 10), None, 1, 15])
        self.assertEqual(connection.commit.call_count, 2)

    def test_lneyra_can_edit_entry_and_exit_but_cannot_view_history(self):
        edit_request = self.factory.post(
            '/marcadores/api/asistencias/editar/',
            data=json.dumps({
                'id_asistencia': 15,
                'hora_ingreso': '08:30',
                'hora_salida': '22:45',
                'motivo': 'Corrección solicitada por RRHH',
            }),
            content_type='application/json',
        )
        edit_request.user = SimpleNamespace(
            is_authenticated=True, is_superuser=False, is_staff=False,
            admin=False, username='lneyra',
        )
        cursor = FakeCursor()
        connection = Mock()
        with patch.object(views, '_get_portalaei_cursor', return_value=cursor), patch.object(
            views, 'connection_portalaei', connection
        ):
            edit_response = views.editar_asistencia(edit_request)

        self.assertEqual(edit_response.status_code, 200)
        update_params = next(
            params for query, params in cursor.executions if 'UPDATE ASISTENCIA' in query
        )
        self.assertEqual(update_params, [time(8, 30), time(22, 45), 2, 15])

        history_request = self.factory.get('/marcadores/api/asistencias/historial/')
        history_request.user = edit_request.user
        history_response = views.historial_modificaciones_asistencia(history_request)
        self.assertEqual(history_response.status_code, 403)

    def test_time_validation_rejects_invalid_values(self):
        with self.assertRaisesRegex(ValueError, 'formato HH:MM'):
            views._parse_attendance_time('25:90', 'La hora')

    def test_nisira_person_lookup_returns_names_and_surnames(self):
        cursor = Mock()
        cursor.fetchone.return_value = ('CARMEN MONICA', 'CRUZ   VELASCO')
        connection = Mock()
        connection.cursor.return_value = cursor

        with patch.object(views, 'open_connection', return_value=connection):
            result = views._lookup_nisira_person('21574732')

        self.assertEqual(result, {
            'nombres': 'CARMEN MONICA',
            'apellidos': 'CRUZ VELASCO',
        })
        self.assertEqual(cursor.execute.call_args.args[1], ['21574732', '21574732'])
        cursor.close.assert_called_once()
        connection.close.assert_called_once()

    def test_existing_placeholder_identity_can_be_updated_from_nisira(self):
        request = self.factory.post(
            '/marcadores/api/asistencias/actualizar-identidad/',
            data=json.dumps({'id_asistencia': 25}),
            content_type='application/json',
        )
        request.user = SimpleNamespace(
            is_authenticated=True, username='JALCANTARA'
        )
        cursor = Mock()
        cursor.fetchone.return_value = (44, '21574732')
        connection = Mock()
        identity = {'nombres': 'CARMEN MONICA', 'apellidos': 'CRUZ VELASCO'}

        with patch.object(views, '_get_portalaei_cursor', return_value=cursor), patch.object(
            views, '_lookup_nisira_person', return_value=identity
        ), patch.object(views, 'connection_portalaei', connection):
            response = views.actualizar_identidad_asistencia(request)

        self.assertEqual(response.status_code, 200)
        update_call = next(
            call for call in cursor.execute.call_args_list
            if 'UPDATE PERSONAL' in call.args[0]
        )
        self.assertEqual(
            update_call.args[1], ['CARMEN MONICA', 'CRUZ VELASCO', 44]
        )
        connection.commit.assert_called_once()

    def test_nisira_xml_contains_code_date_and_time(self):
        xml = _xml_for_marks([{
            'code': '21574732',
            'name': 'PRUEBA & RRHH',
            'timestamp': datetime(2026, 11, 27, 7, 15, 9),
        }])
        self.assertIn('<idcodigogeneral>21574732</idcodigogeneral>', xml)
        self.assertIn('<marcacion>07:15:09</marcacion>', xml)
        self.assertIn('<apenom>PRUEBA  RRHH</apenom>', xml)

    def test_nisira_xml_removes_invalid_ansi_characters(self):
        xml = _xml_for_marks([{
            'code': '12345678', 'name': 'NUÑEZ � TEST',
            'timestamp': datetime(2026, 11, 23, 5, 57, 1),
        }])
        self.assertIn('<apenom>NUNEZ  TEST</apenom>', xml)
        self.assertNotIn('�', xml)

    def test_procedure_reader_skips_intermediate_rowcount(self):
        self.assertEqual(
            _fetch_procedure_rows(FakeProcedureCursor()),
            [('0001', '0002997')],
        )

    def test_non_authorized_user_cannot_sync_nisira(self):
        request = self.factory.post(
            '/marcadores/api/asistencias/sincronizar-nisira/',
            data=json.dumps({'fecha_inicio': '2026-11-27', 'fecha_fin': '2026-11-27', 'sede': 1}),
            content_type='application/json',
        )
        request.user = SimpleNamespace(is_authenticated=True, username='WORKER')
        response = views.sincronizar_asistencias_nisira(request)
        self.assertEqual(response.status_code, 403)

    def test_authorized_sync_uses_selected_period(self):
        request = self.factory.post(
            '/marcadores/api/asistencias/sincronizar-nisira/',
            data=json.dumps({
                'fecha_inicio': '2026-11-26', 'fecha_fin': '2026-11-27',
                'sede': 1, 'empresa': '',
            }),
            content_type='application/json',
        )
        request.user = SimpleNamespace(is_authenticated=True, username='LNEYRA')
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        mark = {'code': '21574732', 'name': 'PRUEBA',
                'timestamp': datetime(2026, 11, 27, 7, 15)}
        with patch.object(views, '_run_portalaei_query', return_value=[mark]), patch.object(
            views, 'synchronize_marks', return_value={
                'sent': 1, 'duplicates': 0, 'types_corrected': 0,
                'warnings': [], 'documents': ['TEST'],
            }
        ) as sync_mock:
            response = views.sincronizar_asistencias_nisira(request)

        self.assertEqual(response.status_code, 200)
        sync_mock.assert_called_once_with(
            [mark], username='LNEYRA', machine='127.0.0.1'
        )

    def test_sync_selected_next_day_sends_only_overnight_exit(self):
        request = self.factory.post(
            '/marcadores/api/asistencias/sincronizar-nisira/',
            data=json.dumps({
                'fecha_inicio': '2026-11-25', 'fecha_fin': '2026-11-25',
                'sede': 1, 'empresa': '',
            }),
            content_type='application/json',
        )
        request.user = SimpleNamespace(is_authenticated=True, username='LNEYRA')
        request.META['REMOTE_ADDR'] = '127.0.0.1'

        class OvernightCursor:
            def execute(self, query, params=None):
                self.query = query
                self.params = params

            def fetchall(self):
                return [(
                    '12345678', 'ANA', 'PRUEBA', date(2026, 11, 24),
                    time(21, 0), time(1, 0),
                )]

        cursor = OvernightCursor()
        captured = {}

        def run_query(callback):
            return callback(cursor)

        def sync_marks(marks, **kwargs):
            captured['marks'] = marks
            return {'sent': 1, 'duplicates': 0, 'types_corrected': 0,
                    'warnings': [], 'documents': ['TEST']}

        with patch.object(views, '_run_portalaei_query', side_effect=run_query), patch.object(
            views, 'synchronize_marks', side_effect=sync_marks
        ):
            response = views.sincronizar_asistencias_nisira(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(cursor.params[:3], [1, date(2026, 11, 25), date(2026, 11, 25)])
        self.assertEqual(len(captured['marks']), 1)
        self.assertEqual(captured['marks'][0]['kind'], 'S')
        self.assertEqual(
            captured['marks'][0]['timestamp'], datetime(2026, 11, 25, 1, 0)
        )

    def test_attendance_filter_returns_overnight_dates_without_datetime_error(self):
        request = self.factory.get(
            '/marcadores/api/asistencias/',
            {'fecha_inicio': '2026-11-24', 'fecha_fin': '2026-11-25', 'sede': '1'},
        )
        overnight_row = (
            91, 10, 1, time(21, 0), time(1, 0), date(2026, 11, 24), 2,
            '12345678', 'ANA', 'PRUEBA', '001', 'AGROSERVICE', 'PLANTA',
        )
        with patch.object(views, '_run_portalaei_query', return_value=[overnight_row]):
            response = views.obtener_asistencias(request)

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload['data'][0]['FECHA_INGRESO'], '2026-11-24')
        self.assertEqual(payload['data'][0]['FECHA_SALIDA'], '2026-11-25')
        self.assertTrue(payload['data'][0]['ES_TURNO_NOCTURNO'])

    def test_next_day_early_mark_closes_overnight_shift(self):
        self.assertTrue(views._is_overnight_exit(
            date(2026, 11, 26), time(21, 0), datetime(2026, 11, 27, 2, 0)
        ))

    def test_old_open_mark_does_not_close_as_overnight_shift(self):
        self.assertFalse(views._is_overnight_exit(
            date(2026, 11, 25), time(21, 0), datetime(2026, 11, 27, 2, 0)
        ))
        self.assertFalse(views._is_overnight_exit(
            date(2026, 11, 26), time(8, 0), datetime(2026, 11, 27, 2, 0)
        ))
        self.assertFalse(views._is_overnight_exit(
            date(2026, 11, 26), time(19, 0), datetime(2026, 11, 27, 9, 0)
        ))
