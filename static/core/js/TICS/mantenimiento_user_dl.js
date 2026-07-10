$(document).ready(function () {
  initUsuariosTable();

  // Manejador para el botón de editar
  $("#usuariosTable").on("click", ".editar-usuario", function () {
    var id = $(this).data("id");
    cargarDatosUsuario(id);
  });

  // Manejador para el botón de eliminar
  $("#usuariosTable").on("click", ".eliminar-usuario", function () {
    var id = $(this).data("id");
    eliminarUsuario(id);
  });

  // Manejador para el botón de agregar nuevo usuario
  $(".btn-agregar").click(function () {
    // Limpiar el formulario
    $("#registerUserForm")[0].reset();
    $("#registerUserForm").removeData("modo usuario-id");
    $("#submitBtn_user").text("Registrar Usuario");
    $("#Modal_Mantenimiento_User .modal-title").text("Registrar Nuevo Usuario");
  });

  // Manejador del formulario para crear/editar usuario
  $("#registerUserForm").submit(function (e) {
    e.preventDefault();

    // Validación de campos requeridos
    const camposRequeridos = ["dni", "nombres", "apaterno", "amaterno"];
    let faltanCampos = false;

    camposRequeridos.forEach((campo) => {
      const valor = $(`#${campo}`).val().trim();
      if (!valor) {
        faltanCampos = true;
        $(`#${campo}`).addClass("is-invalid");
      } else {
        $(`#${campo}`).removeClass("is-invalid");
      }
    });

    if (faltanCampos) {
      Swal.fire({
        icon: "error",
        title: "Error de validación",
        text: "Por favor complete todos los campos requeridos",
      });
      return;
    }

    // Validación específica del DNI
    const dni = $("#dni").val().trim();
    if (!/^\d{8}$/.test(dni)) {
      Swal.fire({
        icon: "error",
        title: "Error de validación",
        text: "El DNI debe contener exactamente 8 dígitos",
      });
      return;
    }

    const formData = {
      dni: dni,
      nombres: $("#nombres").val().trim(),
      apaterno: $("#apaterno").val().trim(),
      amaterno: $("#amaterno").val().trim(),
      celular: $("#celular").val().trim(),
      fecha_naci: $("#fecha_naci").val(),
    };

    const modo = $(this).data("modo");
    const usuarioId = $(this).data("usuario-id");
    let url = "/mantenimiento_user_dl/";
    let type = "POST";

    if (modo === "editar") {
      url = `/mantenimiento_user_dl/${usuarioId}/`;
      type = "PUT";
    }

    // Mostrar indicador de carga
    Swal.fire({
      title: "Procesando...",
      text: "Por favor espere",
      allowOutsideClick: false,
      allowEscapeKey: false,
      showConfirmButton: false,
      didOpen: () => {
        Swal.showLoading();
      },
    });

    $.ajax({
      url: url,
      type: type,
      contentType: "application/json",
      data: JSON.stringify(formData),
      success: function (response) {
        Swal.close();
        $("#Modal_Mantenimiento_User").modal("hide");

        Swal.fire({
          icon: "success",
          title: "Éxito",
          text: response.message,
          showConfirmButton: false,
          timer: 1500,
        });

        // Recargar la tabla y limpiar el formulario
        $("#usuariosTable").DataTable().ajax.reload();
        $("#registerUserForm")[0].reset();
        $("#registerUserForm").removeData("modo usuario-id");
        $("#submitBtn_user").text("Registrar Usuario");
      },
      error: function (xhr) {
        Swal.close();
        const mensaje =
          xhr.responseJSON?.message ||
          "Ocurrió un error al procesar la solicitud";

        Swal.fire({
          icon: "error",
          title: "Error",
          text: mensaje,
        });
      },
    });
  });
});

// Función para inicializar la tabla de usuarios
function initUsuariosTable() {
  var table = $("#usuariosTable").DataTable({
    // Botones de exportación y agregar
    dom: "Bfrtip",
    buttons: [
      {
        text: '<i class="fas fa-sync-alt"></i>',
        className: "btn-sm btn-secondary",
        action: function (e, dt, node, config) {
          // Añadir animación de giro
          $(node).find("i").addClass("fa-spin");

          // Recargar la tabla
          dt.ajax.reload(function () {
            // Callback después de la recarga
            setTimeout(() => {
              $(node).find("i").removeClass("fa-spin");
            }, 1000);
          });
        },
      },
      {
        extend: "excelHtml5",
        title: "Reporte_Usuarios",
        text: '<i class="far fa-file-excel"></i> Excel',
        className: "btn-sm btn-success",
        exportOptions: {
          columns: [0, 1, 2, 3, 4, 5, 6], // Índices de las columnas a exportar
        },
      },
      {
        extend: "pdfHtml5",
        title: "Reporte_Usuarios",
        text: '<i class="far fa-file-pdf"></i> PDF',
        className: "btn-sm btn-danger",
        orientation: "landscape",
        pageSize: "A4",
        exportOptions: {
          columns: [0, 1, 2, 3, 4, 5, 6], // Índices de las columnas a exportar
        },
        customize: function (doc) {
          doc.defaultStyle.fontSize = 8;
          doc.styles.tableHeader.fontSize = 9;
          doc.styles.title.fontSize = 13;
          doc.pageMargins = [20, 20, 20, 20];
        },
      },
      {
        text: '<i class="fas fa-plus mr-1"></i>AGREGAR',
        className: "btn-sm btn-success btn-agregar",
        action: function (e, dt, node, config) {
          $("#Modal_Mantenimiento_User").modal("show");
        },
      },
    ],

    // Configuración de la tabla
    scrollX: true,
    scrollY: "50vh",
    scrollCollapse: true,
    autoWidth: false,
    pageLength: 9,
    responsive: true,
    serverSide: false,
    searching: false,

    columnDefs: [
      { width: "5%", targets: 0 }, // ID
      { width: "10%", targets: 1 }, // DNI
      { width: "15%", targets: 2 }, // Nombres
      { width: "15%", targets: 3 }, // Apellido Paterno
      { width: "15%", targets: 4 }, // Apellido Materno
      { width: "10%", targets: 5 }, // Celular
      { width: "15%", targets: 6 }, // Fecha Nacimiento
      { width: "15%", targets: 7 }, // Acciones
    ],

    // Idioma
    language: {
      url: "//cdn.datatables.net/plug-ins/1.10.25/i18n/Spanish.json",
    },

    // Ajax para obtener los datos
    ajax: {
      url: "/mantenimiento_user_dl/",
      dataSrc: "data",
    },

    // Definición de columnas
    columns: [
      {
        data: "IDUSUARIO",
        title: "ID",
      },
      {
        data: "DNI",
        title: "DNI",
      },
      {
        data: "NOMBRES",
        title: "Nombres",
      },
      {
        data: "APATERNO",
        title: "Apellido Paterno",
      },
      {
        data: "AMATERNO",
        title: "Apellido Materno",
      },
      {
        data: "CELULAR",
        title: "Celular",
      },
      {
        data: "FECHA_NACI",
        title: "Fecha Nacimiento",
      },
      {
        data: null,
        title: "Acciones",
        className: "text-center",
        render: function (data, type, row) {
          return `
                        <button class="btn btn-sm btn-primary editar-usuario" data-id="${row.IDUSUARIO}">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-danger eliminar-usuario" data-id="${row.IDUSUARIO}">
                            <i class="fas fa-trash"></i>
                        </button>
                    `;
        },
      },
    ],

    // Ordenamiento inicial
    order: [[0, "desc"]],
    initComplete: function (settings, json) {
      // Forzar el ajuste de columnas después de la inicialización
      setTimeout(function () {
        table.columns.adjust();
      }, 100);
    },
  });

  // Ajustar cuando el modal se está mostrando
  $("#PresupuestoModalServicios").on("show.bs.modal", function () {
    setTimeout(function () {
      table.columns.adjust();
    }, 50);
  });

  // Ajustar cuando el modal ya está visible
  $("#PresupuestoModalServicios").on("shown.bs.modal", function () {
    setTimeout(function () {
      table.columns.adjust();
    }, 50);
  });
}

// Función para cargar los datos del usuario en el modal
function cargarDatosUsuario(id) {
  $.ajax({
    url: `/mantenimiento_user_dl/${id}/`,
    type: "GET",
    success: function (response) {
      // Llenar el formulario con los datos
      $("#dni").val(response.DNI);
      $("#nombres").val(response.NOMBRES);
      $("#apaterno").val(response.APATERNO);
      $("#amaterno").val(response.AMATERNO);
      $("#celular").val(response.CELULAR);
      $("#fecha_naci").val(response.FECHA_NACI);

      // Modificar el formulario para la edición
      $("#registerUserForm").data("modo", "editar");
      $("#registerUserForm").data("usuario-id", id);
      $("#submitBtn_user").text("Actualizar Usuario");
      $("#Modal_Mantenimiento_User .modal-title").text("Editar Usuario");

      // Mostrar el modal
      $("#Modal_Mantenimiento_User").modal("show");
    },
    error: function (xhr) {
      Swal.fire({
        icon: "error",
        title: "Error",
        text: "No se pudo cargar los datos del usuario",
      });
    },
  });
}

// Función para eliminar usuario
function eliminarUsuario(id) {
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
        url: `/mantenimiento_user_dl/${id}/`,
        type: "DELETE",
        success: function (response) {
          Swal.fire("Eliminado!", response.message, "success").then(() => {
            $("#usuariosTable").DataTable().ajax.reload();
          });
        },
        error: function (xhr) {
          var mensaje = "Error al eliminar el usuario";
          if (xhr.responseJSON && xhr.responseJSON.message) {
            mensaje = xhr.responseJSON.message;
          }

          Swal.fire("Error!", mensaje, "error");
        },
      });
    }
  });
}

function inicializarAutocompletado() {
  $("#nombres")
    .autocomplete({
      source: function (request, response) {
        $.ajax({
          url: "/api_mantenimiento_usuarios_dl/",
          dataType: "json",
          data: {
            q: request.term,
          },
          success: function (data) {
            response(
              data.map(function (item) {
                return {
                  label: `${item.nombres} ${item.apellido_paterno} ${item.apellido_materno}`,
                  value: item.nombres,
                  item: item,
                };
              })
            );
          },
        });
      },
      minLength: 3,
      select: function (event, ui) {
        event.preventDefault();
        $("#nombres").val(ui.item.item.nombres);
        $("#dni").val(ui.item.item.dni);
        $("#apaterno").val(ui.item.item.apellido_paterno);
        $("#amaterno").val(ui.item.item.apellido_materno);
        $("#celular").val(ui.item.item.celular);
        $("#fecha_naci").val(ui.item.item.fecha_nacimiento);
      },
    })
    .autocomplete("instance")._renderItem = function (ul, item) {
    return $("<li>")
      .append(
        `<div class='autocomplete-item'>
            <div class='item-main'>
              <span class='nombre-completo'>${item.label}</span>
            </div>
            <div class='item-details'>
              <span class='detail'>
                <i class='fas fa-id-card'></i> ${item.item.dni}
              </span>
              <span class='detail'>
                <i class='fas fa-phone'></i> ${
                  item.item.celular || "No registrado"
                }
              </span>
            </div>
          </div>`
      )
      .appendTo(ul);
  };

  // Estilos para el autocompletado
  $("<style>")
    .prop("type", "text/css")
    .html(
      `
      .ui-autocomplete {
        max-height: 300px;
        overflow-y: auto;
        overflow-x: hidden;
        z-index: 9999 !important;
        border-radius: 8px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border: 1px solid #e0e0e0;
        padding: 5px;
      }
      .autocomplete-item {
        padding: 10px;
        border-bottom: 1px solid #f0f0f0;
        transition: all 0.2s ease;
      }
      .autocomplete-item:hover {
        background-color: #f8f9fa;
        transform: translateX(5px);
      }
      .item-main {
        margin-bottom: 5px;
      }
      .nombre-completo {
        color: #2c3e50;
        font-weight: 500;
        font-size: 1.1em;
      }
      .item-details {
        display: flex;
        gap: 15px;
        font-size: 0.9em;
        color: #666;
      }
      .detail {
        display: flex;
        align-items: center;
        gap: 5px;
      }
      .detail i {
        color: #3498db;
      }
      .ui-menu-item {
        background: white;
        border: none;
        margin: 2px 0;
      }
      .ui-state-active,
      .ui-widget-content .ui-state-active {
        border: none;
        background: #f8f9fa;
        margin: 0;
      }
    `
    )
    .appendTo("head");
}

// Inicializar cuando el documento esté listo
$(document).ready(function () {
  inicializarAutocompletado();
});
