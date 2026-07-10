from django.shortcuts import render
from django.http import HttpResponse

def evaluacion_fertilidad(request):

    if request.method == 'POST':
        # Aquí recibes TODOS los datos del formulario
        print("=== DATOS RECIBIDOS ===")
        for key, value in request.POST.items():
            print(key, ":", value)

        # Puedes guardar en BD aquí después
        return HttpResponse("Datos guardados correctamente.")

    return render(request, 'PresupuestoAgricola/test_plantilla_evaluacion_form.html')
