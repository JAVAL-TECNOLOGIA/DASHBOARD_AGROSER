from django.shortcuts import render
from django.http import HttpResponse

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connections  # para usar varias bases de datos

def test_plantilla_offline(request):
    return render(request, "PresupuestoAgricola/test_plantilla_offline.html")

@csrf_exempt
def sync_evaluaciones(request):
    if request.method != "POST":
        return JsonResponse({"ok": False, "error": "Método no permitido"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
        items = data.get("items", [])
        synced_ids = []

        with connections['default'].cursor() as cursor:
            for item in items:
                lote = item.get("lote")
                lat = item.get("lat") or None
                lng = item.get("lng") or None
                foto = item.get("foto_base64")

                cursor.execute("""
                    INSERT INTO EVALUACION_OFFLINE (LOTE, LAT, LNG, FOTO_BASE64)
                    VALUES (%s, %s, %s, %s)
                """, [lote, lat, lng, foto])

                synced_ids.append(item.get("id"))

        return JsonResponse({"ok": True, "synced_ids": synced_ids})

    except Exception as e:
        return JsonResponse({"ok": False, "error": str(e)}, status=400)

