$(document).ready(function () {
  // Inicializar componentes
  initFormListeners();

  // Envío del formulario mediante AJAX
  $("#formRegistroCampana").on("submit", function (e) {
    e.preventDefault();

    // Validar el formulario antes de enviar
    if (!validateForm()) {
      return false;
    }

    // Mostrar indicador de carga
    showLoading(true);

    // Obtener datos del formulario
    const formData = new FormData(this);

    // Combinar apellidos y nombres en un solo campo nombreCompleto
    const apellidos = formData.get("apellidos") || "";
    const nombres = formData.get("nombres") || "";

    // Eliminar los campos individuales
    formData.delete("apellidos");
    formData.delete("nombres");

    // Agregar el campo combinado
    formData.append("nombreCompleto", `${apellidos} ${nombres}`.trim());

    // Enviar datos mediante AJAX
    $.ajax({
      url: "/rrhh/api/registro_campana_poda_amarre/",
      type: "POST",
      data: formData,
      processData: false,
      contentType: false,
      success: function (response) {
        showLoading(false);

        // Mostrar mensaje de éxito
        showSuccessMessage(response.message || "Registro completado con éxito");

        // Resetear formulario
        resetForm();

        // Mostrar pantalla de éxito
        showSuccessScreen();
      },
      error: function (xhr) {
        showLoading(false);

        // Mostrar mensaje de error
        let errorMessage = "Ocurrió un error al procesar el registro";

        try {
          const response = JSON.parse(xhr.responseText);
          if (response.message) {
            errorMessage = response.message;
          }
        } catch (e) {
          console.error("Error al parsear respuesta:", e);
        }

        showErrorMessage(errorMessage);
      },
    });
  });

  // Resetear formulario cuando se hace clic en el botón de limpiar
  $('button[type="reset"]').on("click", function () {
    resetFormFields();
    removeValidationStyles();
  });

  // Volver al formulario desde la pantalla de éxito
  $(document).on("click", "#btnNuevoRegistro", function () {
    hideSuccessScreen();
  });
});

// Función para inicializar los listeners del formulario
function initFormListeners() {
  // Mostrar/ocultar campo de texto para "Otro" en labor
  $("#laborOtro").on("change", function () {
    if ($(this).is(":checked")) {
      if ($("#laborOtroTexto").length === 0) {
        $(
          '<input type="text" class="form-control mt-2" id="laborOtroTexto" name="laborOtroTexto" placeholder="Especifique la labor" style="height: 40px; border: 1px solid #e0e0e0; border-radius: 4px; padding: 8px 12px; font-size: 14px;">'
        ).insertAfter($(this).closest(".form-check"));

        // Agregar validación para el campo de texto de Otro
        $("#laborOtroTexto").on("input", function () {
          validateField($(this), $(this).val().trim() !== "");
        });
      }
    } else {
      $("#laborOtroTexto").remove();
    }
  });

  // Mostrar/ocultar campo de texto para "Otro" en lugar de residencia
  $("#lugarResidencia").on("change", function () {
    if ($(this).val() === "OTRO") {
      if ($("#otroLugar").length === 0) {
        $(
          '<input type="text" class="form-control mt-2" id="otroLugar" name="otroLugar" placeholder="Especifique dónde vive" style="height: 40px; border: 1px solid #e0e0e0; border-radius: 4px; padding: 8px 12px; font-size: 14px;">'
        ).insertAfter($(this));

        // Agregar validación para el campo de texto de Otro lugar
        $("#otroLugar").on("input", function () {
          validateField($(this), $(this).val().trim() !== "");
        });
      }
    } else {
      $("#otroLugar").remove();
    }
  });

  // Validación en tiempo real de campos requeridos
  $("input[required], select[required]").on("input change", function () {
    const $field = $(this);
    const isValid = $field.val().trim() !== "";
    validateField($field, isValid);
  });

  // Validación específica para DNI (solo números y longitud = 8)
  $("#dni").on("input", function () {
    const value = $(this).val().replace(/\D/g, ""); // Eliminar no-dígitos
    $(this).val(value); // Actualizar el valor del campo

    const isValid = value.length === 8;
    validateField($(this), isValid);

    if (value.length > 10) {
      $(this).val(value.substring(0, 10)); // Limitar a 8 dígitos
    }
  });

  // Validación específica para celular (solo números)
  $("#celular").on("input", function () {
    const value = $(this).val().replace(/\D/g, ""); // Eliminar no-dígitos
    $(this).val(value); // Actualizar el valor del campo

    const isValid = value.length >= 9;
    validateField($(this), isValid);
  });

  //Validar si es estranjero permitir ingresar mas de 8 digitos en el campo dni
  $("#nacionalidad").on("change", function () {
    if ($(this).val() === "EXTRANJERO") {
      $("#dni").attr("maxlength", "10");
      $("#dni").attr(
        "placeholder",
        "Ingrese su numero de carnet de extranjeria"
      );
    } else {
      $("#dni").attr("maxlength", "8");
      $("#dni").attr("placeholder", "Ingrese su numero de DNI");
    }
  });
  // Validación para correo electrónico (opcional)
  $("#correo").on("input", function () {
    const value = $(this).val().trim();

    // Si está vacío, es válido porque es opcional
    if (value === "") {
      validateField($(this), true);
      return;
    }

    // Validar formato de correo
    const emailRegex = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$/;
    const isValid = emailRegex.test(value);
    validateField($(this), isValid);
  });
}

// Función para validar un campo y mostrar estilos visuales
function validateField($field, isValid) {
  if (isValid) {
    $field.removeClass("is-invalid").addClass("is-valid");
  } else {
    $field.removeClass("is-valid").addClass("is-invalid");
  }
}

// Función para validar todo el formulario antes de enviar
function validateForm() {
  let isValid = true;

  // Validar campos obligatorios
  const requiredFields = [
    { id: "apellidos", message: "Ingrese sus apellidos" },
    { id: "nombres", message: "Ingrese sus nombres" },
    { id: "dni", message: "Ingrese su DNI (8 dígitos)" },
    { id: "nacionalidad", message: "Ingrese su nacionalidad" },
    { id: "celular", message: "Ingrese su número de celular" },
  ];

  // Verificar cada campo requerido
  requiredFields.forEach((field) => {
    const $field = $("#" + field.id);
    const value = $field.val().trim();
    const fieldValid = value !== "";

    validateField($field, fieldValid);

    if (!fieldValid) {
      isValid = false;
      showFieldError($field, field.message);
    }
  });

  // Validación específica para DNI
  /* const dniValue = $("#dni").val().trim();
  if (dniValue.length !== 8 && dniValue.length !== 10) {
    validateField($("#dni"), false);
    showFieldError($("#dni"), "El DNI debe tener 8 dígitos o 10 dígitos");
    isValid = false;
  }
 */
  // Validar que se seleccionó una labor
  if (!$('input[name="labor"]:checked').length) {
    showErrorMessage("Seleccione la labor a la que postula");
    isValid = false;
  }

  // Si se seleccionó "OTRO" en labor, validar que se especificó cuál
  if (
    $("#laborOtro").is(":checked") &&
    $("#laborOtroTexto").val().trim() === ""
  ) {
    validateField($("#laborOtroTexto"), false);
    showFieldError($("#laborOtroTexto"), "Especifique la labor");
    isValid = false;
  }

  // Validar que se seleccionó un lugar de residencia
  const lugarResidencia = $("#lugarResidencia").val();
  if (!lugarResidencia || lugarResidencia === "") {
    validateField($("#lugarResidencia"), false);
    showFieldError($("#lugarResidencia"), "Seleccione donde vive");
    isValid = false;
  }

  // Si se seleccionó "OTRO" en lugar de residencia, validar que se especificó cuál
  if (lugarResidencia === "OTRO" && $("#otroLugar").val().trim() === "") {
    validateField($("#otroLugar"), false);
    showFieldError($("#otroLugar"), "Especifique dónde vive");
    isValid = false;
  }

  // Validar formato de correo si se ingresó (opcional)
  const correoValue = $("#correo").val().trim();
  if (correoValue !== "") {
    const emailRegex = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$/;
    if (!emailRegex.test(correoValue)) {
      validateField($("#correo"), false);
      showFieldError($("#correo"), "Ingrese un correo electrónico válido");
      isValid = false;
    }
  }

  return isValid;
}

// Mostrar mensaje de error junto a un campo
function showFieldError($field, message) {
  // Eliminar mensajes de error previos
  $field.siblings(".invalid-feedback").remove();

  // Agregar nuevo mensaje de error
  $field.after(
    `<div class="invalid-feedback" style="display: block;">${message}</div>`
  );
}

// Mostrar mensaje de error general
function showErrorMessage(message) {
  // Eliminar mensajes previos
  $(".alert-danger").remove();

  // Agregar el nuevo mensaje
  const alertHtml = `
        <div class="alert alert-danger alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                <span aria-hidden="true">&times;</span>
            </button>
        </div>
    `;

  $("#formRegistroCampana").before(alertHtml);

  // Scroll al mensaje
  $("html, body").animate(
    {
      scrollTop: $(".alert-danger").offset().top - 100,
    },
    500
  );
}

// Mostrar mensaje de éxito
function showSuccessMessage(message) {
  // Eliminar mensajes previos
  $(".alert-success").remove();

  // Agregar el nuevo mensaje
  const alertHtml = `
        <div class="alert alert-success alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                <span aria-hidden="true">&times;</span>
            </button>
        </div>
    `;

  $("#formRegistroCampana").before(alertHtml);

  // Scroll al mensaje
  $("html, body").animate(
    {
      scrollTop: $(".alert-success").offset().top - 100,
    },
    500
  );
}

// Mostrar u ocultar indicador de carga
function showLoading(show) {
  if (show) {
    // Deshabilitar botones
    $("#formRegistroCampana button").prop("disabled", true);

    // Mostrar spinner en el botón de envío
    $('#formRegistroCampana button[type="submit"]').html(
      '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Enviando...'
    );
  } else {
    // Habilitar botones
    $("#formRegistroCampana button").prop("disabled", false);

    // Restaurar texto del botón de envío
    $('#formRegistroCampana button[type="submit"]').html(
      '<i class="fas fa-check-circle me-2"></i> Registrar'
    );
  }
}

// Resetear el formulario a su estado inicial
function resetForm() {
  $("#formRegistroCampana")[0].reset();
  removeValidationStyles();
  $("#laborOtroTexto, #otroLugar").remove();
}

// Eliminar todos los estilos de validación
function removeValidationStyles() {
  $(".is-valid, .is-invalid").removeClass("is-valid is-invalid");
  $(".invalid-feedback").remove();
}

// Resetear solo los campos (sin restablecer estilos)
function resetFormFields() {
  $("#formRegistroCampana")[0].reset();
  $("#laborOtroTexto, #otroLugar").remove();
}

// Función para mostrar la pantalla de éxito
function showSuccessScreen() {
  // Ocultar formulario
  $(".form-container form").hide();

  // Crear y mostrar pantalla de éxito si no existe
  if ($("#successScreen").length === 0) {
    const successHtml = `
      <div id="successScreen" class="text-center my-4">
        <div style="width: 80px; height: 80px; margin: 0 auto; background-color: #1ab069; color: white; border-radius: 50%; display: flex; justify-content: center; align-items: center;">
          <i class="fas fa-check" style="font-size: 40px;"></i>
        </div>
        <h4 class="mt-3 text-success">¡Registro Exitoso!</h4>
        <p>Gracias por tu interés en formar parte de la familia Don Luis. Pronto nos pondremos en contacto contigo.</p>
        <button type="button" id="btnNuevoRegistro" class="btn text-white px-4 mt-3" style="background-color: #1ab069;">
          Registrar nueva persona
        </button>
      </div>
    `;

    $(".form-container form").after(successHtml);
  } else {
    $("#successScreen").show();
  }
}

// Función para ocultar la pantalla de éxito
function hideSuccessScreen() {
  $("#successScreen").hide();
  $(".form-container form").show();
  resetForm();
}
