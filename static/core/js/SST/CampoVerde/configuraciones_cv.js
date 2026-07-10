function cargarConfiguraciones() {
  $.ajax({
    url: "/configuraciones-sueldos-salarios/",
    method: "GET",
    success: function (response) {
      if (response) {
        // Mostrar los valores decimales directamente
        $("#tasaSueldo").val(response.tasa_carga_social_sueldo.toFixed(4));
        $("#tasaSalario").val(response.tasa_carga_social_salario.toFixed(4));

        // Asegurarse de que el sueldo mínimo se muestre con dos decimales
        if (response.sueldo_minimo !== undefined) {
          $("#sueldoMinimo").val(parseFloat(response.sueldo_minimo).toFixed(2));
        } else {
          $("#sueldoMinimo").val("1025.00"); // Valor por defecto si no existe
        }

        $("#montoTransporte").val(
          parseFloat(response.monto_transporte).toFixed(2)
        );
        $("#montoAlimentacion").val(
          parseFloat(response.monto_alimentacion).toFixed(2)
        );

        // Actualizar la información de última actualización
        if (response.fecha_actualizacion) {
          const fecha = new Date(response.fecha_actualizacion);
          const opciones = {
            year: "numeric",
            month: "long",
            day: "numeric",
            hour: "2-digit",
            minute: "2-digit",
          };
          $("#ultimaActualizacion").text(
            fecha.toLocaleDateString("es-ES", opciones)
          );
          $("#usuarioActualizacion").text(
            response.usuario_actualizacion || "-"
          );
        }
      }
    },
    error: function (xhr, status, error) {
      console.error("Error al cargar configuraciones:", error);
      Swal.fire({
        icon: "warning",
        title: "Error",
        text: "No se pudieron cargar las configuraciones",
      });
    },
  });
}

function actualizarConfiguraciones() {
  const tasaSueldo = parseFloat($("#tasaSueldo").val());
  const tasaSalario = parseFloat($("#tasaSalario").val());
  const sueldoMinimo = parseFloat($("#sueldoMinimo").val());
  const montoTransporte = parseFloat($("#montoTransporte").val());
  const montoAlimentacion = parseFloat($("#montoAlimentacion").val());
  // Validar valores decimales
  if (
    isNaN(tasaSueldo) ||
    tasaSueldo < 0 ||
    tasaSueldo > 1 ||
    isNaN(tasaSalario) ||
    tasaSalario < 0 ||
    tasaSalario > 1
  ) {
    Swal.fire({
      icon: "error",
      title: "Error",
      text: "Por favor ingrese tasas válidas (entre 0 y 1)",
    });
    return;
  }

  if (isNaN(sueldoMinimo) || sueldoMinimo <= 0) {
    Swal.fire({
      icon: "error",
      title: "Error",
      text: "Por favor ingrese un sueldo mínimo válido",
    });
    return;
  }
  const data = {
    tasa_carga_social_sueldo: tasaSueldo,
    tasa_carga_social_salario: tasaSalario,
    sueldo_minimo: sueldoMinimo,
    monto_transporte: montoTransporte,
    monto_alimentacion: montoAlimentacion,
  };

  Swal.fire({
    title: "¿Estás seguro?",
    text: "Se actualizarán las configuraciones",
    icon: "warning",
    showCancelButton: true,
    confirmButtonText: "Sí, guardar cambios",
    cancelButtonText: "Cancelar",
  }).then((result) => {
    if (result.isConfirmed) {
      $.ajax({
        url: "/configuraciones-sueldos-salarios/",
        method: "PUT",
        data: JSON.stringify(data),
        contentType: "application/json",
        success: function (response) {
          Swal.fire({
            icon: "success",
            title: "¡Actualizado!",
            text: "Las configuraciones se han guardado correctamente",
            timer: 1500,
          });
          cargarConfiguraciones();
        },
        error: function (xhr, status, error) {
          console.error("Error al actualizar:", error);
          Swal.fire({
            icon: "error",
            title: "Error",
            text: "No se pudieron guardar los cambios: " + error,
          });
        },
      });
    }
  });
}

document.addEventListener("DOMContentLoaded", function () {
  cargarConfiguraciones();
});
