from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

from apps.connection.connect_portalaei import connection_portalaei

def evaluacion_fertilidad(request):
    return render(request, 'PresupuestoAgricola/consolidado/consolidado_main.html')

def compras_lotes_api(request):
    with connection_portalaei.cursor() as cursor:
        cursor.execute("""
            SELECT
                sector,
                condicion,
                lote,
                area_total,
                variedad,
                plantas_lote,
                plantas_ha,

                compost_guano,
                sulfato_calcio,
                total_mo,

                en_formacion_agro,
                en_formacion_ferti,
                en_formacion_total,

                post_agro,
                post_ferti,
                post_total,

                repoda,
                prod_agro,
                prod_ferti,
                prod_total,

                combustible,
                plantulas,
                repuestos,

                total_lote
            FROM dbo.vw_compras_lotes
            ORDER BY sector, lote
        """)

        columns = [col[0] for col in cursor.description]
        data = [dict(zip(columns, row)) for row in cursor.fetchall()]

    return JsonResponse({"data": data})