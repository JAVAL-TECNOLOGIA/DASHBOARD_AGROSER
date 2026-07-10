from django.views.generic import TemplateView
from django.http import JsonResponse
from datetime import datetime
from apps.connection.connect_donluis import connection_donluis
from django.views import View

class Fito_apl_diario(TemplateView):
    template_name = 'FITOSANIDAD/fito_apl_diario.html'


class Fito_apl_diario_script(View):
    
    def get(self, request, *args, **kwargs):

        with connection_donluis.cursor() as cursor:
            cursor.execute('''
                SELECT 
                    R.IDRECOMENDACIONAPL AS IDENTIFICADOR,
                    A.DESCRIPCION AS ALMACEN,
                    S.DESCRIPCION AS SUCURSAL,
                    R.FECHA,
                    CONCAT(R.IDDOCUMENTO, ' - ', R.SERIE, ' - ', R.NUMERO) AS DOCUMENTO,
                    C.DESCRIPCION AS CONSUMIDOR,
                    RE.NOMBRE AS RESPONSABLE,
                    CASE R.IDESTADO
                        
                        WHEN 'AP' THEN 'Aprobado'
                        WHEN 'PE' THEN 'Pendiente'
                        WHEN 'RE' THEN 'Rechazado'
                    
                    END AS ESTADO_DESCRIPCION
                FROM RECOMENDACIONAPL R (NOLOCK)
                LEFT JOIN ALMACENES A (NOLOCK) ON R.IDALMACEN = A.IDALMACEN AND R.IDEMPRESA = A.IDEMPRESA
                LEFT JOIN SUCURSALES S (NOLOCK) ON R.IDSUCURSAL = S.IDSUCURSAL AND R.IDEMPRESA = S.IDEMPRESA
                LEFT JOIN CONSUMIDOR C (NOLOCK) ON R.IDCONSUMIDOR = C.IDCONSUMIDOR AND R.IDEMPRESA = C.IDEMPRESA
                LEFT JOIN RESPONSABLE RE (NOLOCK) ON R.IDRESPONSABLE = RE.IDRESPONSABLE AND R.IDEMPRESA = RE.IDEMPRESA 
                ORDER BY R.FECHA DESC  

                          ''')
            data_object = cursor.fetchall()
            cursor.close
        data_json = []
        for data in data_object:
            data_json.append({'IDENTIFICADOR':data[0],
                'ALMACEN':data[1],
                'SUCURSAL':data[2],
                'FECHA':data[3],
                'DOCUMENTO':data[4],
                'CONSUMIDOR':data[5],
                'RESPONSABLE':data[6],
                'ESTADO_DESCRIPCION':data[7]})
        return JsonResponse(data_json, safe=False)



class Fito_apl_diario_detalles(View):
    def get(self, request, identificador, *args, **kwargs):
        with connection_donluis.cursor() as cursor:
            # Cambiamos la forma de ejecutar el procedimiento almacenado
            cursor.execute("EXEC FORM_APLI_FITOSANITARIA @ID_APL_FITO = ?", (identificador,))
            columns = [column[0] for column in cursor.description]
            detalles = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        if detalles:
            return JsonResponse(detalles, safe=False)
        else:
            return JsonResponse({'error': 'No se encontraron detalles para el identificador proporcionado'}, status=404)