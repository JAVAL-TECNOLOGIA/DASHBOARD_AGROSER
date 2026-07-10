$(document).ready(function () {
  // Inicializar la tabla y los componentes
  initTrabajadoresTable();

  cargarSelectores();

  // Manejar el botón de expandir
  $('[data-click="panel-expand"]').click(function (e) {
    e.stopPropagation();
    handlePanelExpand();
  });

  // Manejar el botón de recargar
  $('[data-click="panel-reload"]').click(function (e) {
    e.stopPropagation();
    handlePanelReload();
  });

  // Manejar el botón de cerrar
  $('[data-click="panel-remove"]').click(function (e) {
    e.stopPropagation();
    $("#modal_mant_trabajador").modal("hide");
  });

  //=========================================================================================
  // Limpiar el formulario cuando se cierre el modal
  //=========================================================================================

  // Evento cuando se cierra el modal (por cualquier medio)
  $("#Modal_Mantenimiento_Trabajador").on("hidden.bs.modal", function () {
    limpiarFormularioTrabajador();
  });

  // Evento para el botón cancelar
  $("#Modal_Mantenimiento_Trabajador .btn-secondary").click(function () {
    $("#Modal_Mantenimiento_Trabajador").modal("hide");
  });

  // Evento para el botón X (cerrar) del modal
  $("#Modal_Mantenimiento_Trabajador .close").click(function () {
    $("#Modal_Mantenimiento_Trabajador").modal("hide");
  });

  async function cargarSelectores() {
    try {
      // Inicializar usuario select2 primero
      initializeUserSelect();

      // Cargar datos secuencialmente
      await cargarSelector("cargo");
      await cargarSelector("area");
      await cargarSelector("gerencia");
      await cargarSelector("sede");
      await cargarSelector("empresa");
    } catch (error) {
      console.error("Error al cargar selectores:", error);
      Swal.fire({
        icon: "error",
        title: "Error",
        text: "Hubo un problema al cargar algunos datos",
      });
    }
  }
});

// Inicializar DataTable
function initTrabajadoresTable() {
  var table = $("#trabajadoresTable").DataTable({
    dom: "Bfrtip",
    buttons: [
      {
        extend: "excel",
        text: '<i class="fas fa-file-excel"></i> Excel',
        className: "btn-sm btn-success",
        exportOptions: {
          columns: ":visible",
        },
      },
      {
        extend: "pdf",
        text: '<i class="far fa-file-pdf"></i> PDF',
        className: "btn-sm btn-danger",
        orientation: "landscape",
        pageSize: "A4",
        exportOptions: {
          columns: ":visible",
        },
      },
      {
        text: '<i class="fas fa-plus mr-1"></i>AGREGAR',
        className: "btn-sm btn-success btn-agregar",
        action: function (e, dt, node, config) {
          limpiarFormularioTrabajador();
          $("#Modal_Mantenimiento_Trabajador").modal("show");
        },
      },
    ],
    ajax: {
      url: "/trabajador/",
      dataSrc: "data",
    },
    scrollX: true,
    scrollY: "250px",
    scrollCollapse: true,
    autoWidth: true,
    pageLength: 9,
    responsive: true,
    serverSide: false,
    searching: false,

    columns: [
      { data: "idtrabajador", title: "ID" },
      { data: "nombre_usuario", title: "Nombre", minWidth: "200px" },
      { data: "cargo", title: "Cargo" },
      { data: "area", title: "Area" },
      { data: "gerencia", title: "Gerencia" },
      { data: "sede", title: "Sede" },
      { data: "empresa", title: "Empresa" },
      {
        data: null,
        title: "Acciones",
        render: function (data, type, row) {
          return `
                        <button class="btn btn-sm btn-primary editar-trabajador" data-id="${row.idtrabajador}">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-danger eliminar-trabajador" data-id="${row.idtrabajador}">
                            <i class="fas fa-trash"></i>
                        </button>
                    `;
        },
      },
    ],
    language: {
      url: "//cdn.datatables.net/plug-ins/1.10.25/i18n/Spanish.json",
    },

    initComplete: function (settings, json) {
      // Forzar el ajuste de columnas después de la inicialización
      setTimeout(function () {
        table.columns.adjust();
      }, 100);
    },
  });

  // Ajustar cuando el modal se está mostrando
  $("#modal_mant_trabajador").on("show.bs.modal", function () {
    setTimeout(function () {
      table.columns.adjust();
    }, 50);
  });

  // Ajustar cuando el modal ya está visible
  $("#modal_mant_trabajador").on("shown.bs.modal", function () {
    setTimeout(function () {
      table.columns.adjust();
    }, 50);
  });
}

function initializeUserSelect() {
  $("#idusuario").select2({
    theme: "bootstrap-5",
    dropdownParent: $("#Modal_Mantenimiento_Trabajador"),
    width: "100%",
    ajax: {
      url: "/mantenimiento_user_dl/",
      dataType: "json",
      delay: 250,
      data: function (params) {
        return {
          search: params.term || "",
        };
      },
      processResults: function (data, params) {
        let results = data.data;

        if (params.term) {
          const searchTerm = params.term.toLowerCase();
          results = results.filter((item) => {
            const fullName = (
              item.NOMBRES +
              " " +
              item.APATERNO +
              " " +
              item.AMATERNO
            ).toLowerCase();
            const dni = item.DNI.toString().toLowerCase();
            return fullName.includes(searchTerm) || dni.includes(searchTerm);
          });
        }

        return {
          results: results.map((item) => ({
            id: item.IDUSUARIO,
            text:
              item.NOMBRES +
              " " +
              item.APATERNO +
              " " +
              item.AMATERNO +
              " - " +
              item.DNI,
            dni: item.DNI,
          })),
        };
      },
      cache: true,
    },
    placeholder: "Buscar por nombre o DNI...",
    allowClear: true,
    minimumInputLength: 1,
    language: {
      inputTooShort: function () {
        return "Ingrese al menos un carácter";
      },
      searching: function () {
        return "Buscando...";
      },
      noResults: function () {
        return "No se encontraron resultados";
      },
      errorLoading: function () {
        return "Error al cargar los resultados";
      },
    },
  });
}

function cargarSelector(tipo, intentoActual = 1, maxIntentos = 3) {
  const config = {
    cargo: { url: "/api/cargos/", key: "cargos" },
    area: { url: "/api/areas/", key: "areas" },
    gerencia: { url: "/api/gerencias/", key: "gerencias" },
    sede: { url: "/api/sedes/", key: "sedes" },
    empresa: { url: "/api/empresas/", key: "empresas" },
  };

  return new Promise((resolve, reject) => {
    const select = $(`#id${tipo}`);
    select
      .prop("disabled", true)
      .empty()
      .append('<option value="">Cargando...</option>');

    $.ajax({
      url: config[tipo].url,
      type: "GET",
      timeout: 5000, // Timeout de 5 segundos
      success: function (response) {
        select
          .empty()
          .append(`<option value="">Seleccione un/a ${tipo}</option>`);

        response[config[tipo].key].forEach(function (item) {
          select.append(
            `<option value="${item.id}">${item.descripcion}</option>`
          );
        });

        select.select2({
          theme: "bootstrap-5",
          dropdownParent: $("#Modal_Mantenimiento_Trabajador"),
          width: "100%",
          placeholder: `Seleccione un/a ${tipo}`,
          allowClear: true,
        });

        resolve();
      },
      error: function (xhr, status, error) {
        console.error(
          `Error al cargar ${tipo} (intento ${intentoActual}):`,
          error
        );

        if (intentoActual < maxIntentos) {
          // Esperar antes de reintentar (tiempo exponencial)
          const tiempoEspera = Math.min(
            1000 * Math.pow(2, intentoActual - 1),
            5000
          );

          setTimeout(() => {
            cargarSelector(tipo, intentoActual + 1, maxIntentos)
              .then(resolve)
              .catch(reject);
          }, tiempoEspera);
        } else {
          Swal.fire({
            icon: "error",
            title: "Error de carga",
            text: `No se pudo cargar ${tipo}. ¿Desea intentar nuevamente?`,
            showCancelButton: true,
            confirmButtonText: "Reintentar",
            cancelButtonText: "Cancelar",
          }).then((result) => {
            if (result.isConfirmed) {
              cargarSelector(tipo, 1, maxIntentos).then(resolve).catch(reject);
            } else {
              reject(
                `No se pudo cargar ${tipo} después de ${maxIntentos} intentos`
              );
            }
          });
        }
      },
      complete: function () {
        select
          .prop("disabled", false)
          .find('option:contains("Cargando...")')
          .remove();
      },
    });
  });
}

// Modificar la función cargarSelectores para usar el nuevo sistema
async function cargarSelectores() {
  try {
    Swal.fire({
      title: "Cargando datos...",
      text: "Por favor espere...",
      allowOutsideClick: false,
      didOpen: () => {
        Swal.showLoading();
      },
    });

    // Inicializar usuario select2 primero
    await initializeUserSelect();

    // Cargar los demás selectores en paralelo
    await Promise.all([
      cargarSelector("cargo"),
      cargarSelector("area"),
      cargarSelector("gerencia"),
      cargarSelector("sede"),
      cargarSelector("empresa"),
    ]);

    Swal.close();
  } catch (error) {
    console.error("Error al cargar selectores:", error);
    Swal.fire({
      icon: "error",
      title: "Error",
      text: "Hubo un problema al cargar algunos datos. ¿Desea intentar nuevamente?",
      showCancelButton: true,
      confirmButtonText: "Reintentar",
      cancelButtonText: "Cancelar",
    }).then((result) => {
      if (result.isConfirmed) {
        cargarSelectores();
      }
    });
  }
}

//=========================================================================================
// Manejar el formulario de agregar/editar trabajador
//=========================================================================================
// Editar trabajador
$(document).on("click", ".editar-trabajador", function () {
  const id = $(this).data("id");

  // Mostrar loader
  Swal.fire({
    title: "Cargando...",
    allowOutsideClick: false,
    didOpen: () => {
      Swal.showLoading();
    },
  });

  // Obtener datos del trabajador
  $.get(`/trabajador/${id}/`, function (data) {
    // Establecer ID del trabajador
    $("#idtrabajador").val(data.idtrabajador);

    // Configurar select2 para usuario
    const usuarioOption = new Option(
      data.nombre_usuario,
      data.idusuario,
      true,
      true
    );
    $("#idusuario").empty().append(usuarioOption).trigger("change");

    // Establecer valores en los demás selectores
    $("#idcargo").val(data.idcargo).trigger("change");
    $("#idarea").val(data.idarea).trigger("change");
    $("#idgerencia").val(data.idgerencia).trigger("change");
    $("#idsede").val(data.idsede).trigger("change");
    $("#idempresa").val(data.idempresa).trigger("change");

    // Mostrar el modal
    $("#Modal_Mantenimiento_Trabajador").modal("show");

    // Cerrar el loader
    Swal.close();
  }).fail(function (xhr, status, error) {
    Swal.fire({
      icon: "error",
      title: "Error",
      text: "No se pudo cargar la información del trabajador",
    });
    console.error("Error al cargar trabajador:", error);
  });
});

// Guardar/Actualizar trabajador
$("#trabajadorForm").submit(function (e) {
  e.preventDefault();

  const formData = {
    idusuario: $("#idusuario").val(),
    idcargo: $("#idcargo").val(),
    idarea: $("#idarea").val(),
    idgerencia: $("#idgerencia").val(),
    idsede: $("#idsede").val(),
    idempresa: $("#idempresa").val(),
  };

  // Validación de campos requeridos
  const camposRequeridos = [
    "idusuario",
    "idcargo",
    "idarea",
    "idgerencia",
    "idsede",
    "idempresa",
  ];
  const camposFaltantes = camposRequeridos.filter((campo) => !formData[campo]);

  if (camposFaltantes.length > 0) {
    const camposTexto = camposFaltantes
      .map(
        (campo) =>
          campo.replace("id", "").charAt(0).toUpperCase() +
          campo.replace("id", "").slice(1)
      )
      .join(", ");

    Swal.fire({
      icon: "warning",
      title: "Campos incompletos",
      text: `Por favor, complete los siguientes campos: ${camposTexto}`,
      confirmButtonText: "Entendido",
      confirmButtonColor: "#3085d6",
    });
    return;
  }

  // Verificar si es edición o nuevo registro
  const isEdit = !!$("#idtrabajador").val();
  if (isEdit) {
    formData.idtrabajador = $("#idtrabajador").val();
  }

  // Mostrar loader mientras procesa
  Swal.fire({
    title: "Procesando...",
    allowOutsideClick: false,
    didOpen: () => {
      Swal.showLoading();
    },
  });

  $.ajax({
    url: isEdit ? `/trabajador/${formData.idtrabajador}/` : "/trabajador/",
    type: isEdit ? "PUT" : "POST",
    data: JSON.stringify(formData),
    contentType: "application/json",
    success: function (response) {
      Swal.fire({
        icon: "success",
        title: "Éxito",
        text: isEdit
          ? "Trabajador actualizado correctamente"
          : "Trabajador agregado correctamente",
        showConfirmButton: false,
        timer: 1500,
      });

      $("#Modal_Mantenimiento_Trabajador").modal("hide");
      limpiarFormularioTrabajador();
      $("#trabajadoresTable").DataTable().ajax.reload();
    },
    error: function (xhr, status, error) {
      let mensajeError = "Error al procesar la solicitud";

      if (xhr.responseJSON) {
        if (
          xhr.responseJSON.error === "Ya existe un registro para este usuario"
        ) {
          mensajeError = "Este usuario ya está registrado como trabajador";
        } else if (xhr.responseJSON.message) {
          mensajeError = xhr.responseJSON.message;
        }
      }

      Swal.fire({
        icon: "error",
        title: "Error",
        text: mensajeError,
        confirmButtonText: "Entendido",
        confirmButtonColor: "#3085d6",
      });
    },
  });
});

//=========================================================================================
// Eliminar trabajador
//=========================================================================================
$(document).on("click", ".eliminar-trabajador", function () {
  const id = $(this).data("id");
  Swal.fire({
    title: "¿Está seguro?",
    text: "Esta acción no se puede revertir",
    icon: "warning",
    showCancelButton: true,
    confirmButtonColor: "#3085d6",
    cancelButtonColor: "#d33",
    confirmButtonText: "Sí, eliminar",
    cancelButtonText: "Cancelar",
  }).then((result) => {
    if (result.isConfirmed) {
      $.ajax({
        url: `/trabajador/${id}/`,
        type: "DELETE",
        success: function (response) {
          Swal.fire({
            icon: "success",
            title: "Eliminado",
            text: "Trabajador eliminado correctamente",
            showConfirmButton: false,
            timer: 1500,
          });
          $("#trabajadoresTable").DataTable().ajax.reload();
        },
        error: function (xhr) {
          Swal.fire({
            icon: "error",
            title: "Error",
            text:
              xhr.responseJSON?.message || "Error al eliminar el trabajador",
          });
        },
      });
    }
  });
});

// Editar trabajador
$(document).on("click", ".editar-trabajador", function () {
  const id = $(this).data("id");
  $.get(`/trabajador/${id}/`, function (data) {
    $("#idtrabajador").val(data.idtrabajador);
    $("#idusuario").val(data.idusuario).trigger("change");
    $("#idcargo").val(data.idcargo).trigger("change");
    $("#idarea").val(data.idarea).trigger("change");
    $("#idgerencia").val(data.idgerencia).trigger("change");
    $("#idsede").val(data.idsede).trigger("change");
    $("#idempresa").val(data.idempresa).trigger("change");
    $("#Modal_Mantenimiento_Trabajador").modal("show");
  });
});

// Funciones auxiliares para el panel
function handlePanelExpand() {
  const modal = $("#modal_mant_trabajador");
  const modalDialog = modal.find(".modal-dialog");
  const modalContent = modal.find(".modal-content");

  if (modal.hasClass("modal-fullscreen")) {
    // Restaurar tamaño original
    modal.removeClass("modal-fullscreen");
    modalDialog.css({
      "max-width": "60%",
      width: "60%",
      margin: "1.75rem auto",
    });
  } else {
    // Expandir a pantalla completa
    modal.addClass("modal-fullscreen");
    modalDialog.css({
      "max-width": "100%",
      width: "100%",
      margin: "0",
    });
  }

  $("#trabajadoresTable").DataTable().columns.adjust();
}

function handlePanelReload() {
  const panel = $(this).closest(".modal-content");
  panel.append(
    '<div class="panel-loader"><span class="spinner-border spinner-border-sm"></span></div>'
  );

  setTimeout(function () {
    $(".panel-loader", panel).remove();
    $("#trabajadoresTable").DataTable().ajax.reload();
  }, 500);
}

//=========================================================================================
// Función para limpiar el formulario
//=========================================================================================
function limpiarFormularioTrabajador() {
  // Limpiar el formulario base
  $("#trabajadorForm")[0].reset();

  // Limpiar el ID de trabajador (en caso de edición)
  $("#idtrabajador").val("");

  // Limpiar y resetear todos los select2
  $("#idusuario").val(null).trigger("change");

  // Limpiar los demás selectores
  const selectores = ["cargo", "area", "gerencia", "sede", "empresa"];
  selectores.forEach((tipo) => {
    $(`#id${tipo}`).val(null).trigger("change");
  });
}
