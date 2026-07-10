if (typeof window.presupuestoMaterialesInitialized === "undefined") {
  window.presupuestoMaterialesInitialized = true;

  let table; // DataTable para Sueldos
  let tableSalarios; // DataTable para Salarios

  // Variables globales de configuración
  let tasaCargaSocialSueldo = 0.443; // Valor por defecto, se actualiza luego por AJAX
  let sueldoMinimo = 1025.0; // Valor por defecto
  let montoTransporte = 6.51; // Valor por defecto
  let montoAlimentacion = 5.05; // Valor por defecto

  let tasaCargaSocialSalario = 0.443; // Para salarios
  let montoTransporteSalario = 6.51; // Para salarios
  let montoAlimentacionSalario = 5.05; // Para salarios

  //-------------------------------------------------------------------------------
  // SECCIÓN PRINCIPAL: Se ejecuta al cargar el documento (una sola vez)
  //-------------------------------------------------------------------------------
  $(document).ready(function () {
    //-----------------------------------
    // 1) INICIALIZAR AUTOCOMPLETE
    //-----------------------------------
    inicializarAutocompleteDNI();
    inicializarAutocompleteDNI_Salario();

    //-----------------------------------
    // 2) INICIALIZAR EVENTOS GENERALES
    //-----------------------------------
    // Checkbox Asignación Familiar (SUELDO)
    $("#check_asignacion_familiar").on("change", function () {
      calcularAsignacionFamiliar();
    });
    // Checkbox Asignación Familiar (SALARIO)
    $("#check_asignacion_familiar_salario").on("change", function () {
      calcularAsignacionFamiliar_Salarios();
    });

    // Switches de meses (Sueldo)
    $('input[type="checkbox"][id$="_switch_sueldo"]').on("change", function () {
      var mesId = this.id.replace("_switch_sueldo", "");
      $("#" + mesId + "_cantidad_sueldo").prop("disabled", !this.checked);
      actualizarTotalAnual();
    });
    // Switches de meses (Salario)
    $('input[type="checkbox"][id$="_switch_salario"]').on(
      "change",
      function () {
        var mesId = this.id.replace("_switch_salario", "");
        $("#" + mesId + "_cantidad_salario").prop("disabled", !this.checked);
        actualizarTotalAnual_Salarios();
      }
    );

    // Inputs de cantidad por mes
    $(".cantidad-mes-sueldo").on("input", actualizarTotalAnual);
    $(".cantidad-mes-salario").on("input", actualizarTotalAnual_Salarios);

    // Botones de recarga
    $("#recargarSalarios").on("click", function (e) {
      e.stopPropagation();
      $(this).find("i").addClass("fa-spin");
      actualizarTotalSalarios();
      setTimeout(() => {
        $(this).find("i").removeClass("fa-spin");
      }, 1000);
    });
    $("#recargarSueldos").on("click", function (e) {
      e.stopPropagation();
      $(this).find("i").addClass("fa-spin");
      actualizarTotalSueldos();
      setTimeout(() => {
        $(this).find("i").removeClass("fa-spin");
      }, 1000);
    });

    // Eventos de vacación (Sueldo)
    $(".vacaciones-checkbox-sueldoSalario").on("change", function () {
      const mes = this.id.replace("_vacaciones_sueldoSalario", "");
      const switchElement = $(`#${mes}_switch_sueldo`);
      const inputElement = $(`#${mes}_cantidad_sueldo`);
      const container = $(this).closest(".custom-switch-container");
      let mesVacaciones = "0";

      if (this.checked) {
        container.addClass("vacaciones");
        mesVacaciones = obtenerNumeroMes(mes);
        switchElement.prop("disabled", true);

        if (switchElement.is(":checked")) {
          inputElement.data("valor-previo", inputElement.val());
        }
        switchElement.prop("checked", false).trigger("change");
        inputElement.prop("disabled", true).val("");

        // Deshabilitar los demás checkboxes de vacaciones
        $(".vacaciones-checkbox-sueldoSalario")
          .not(this)
          .prop("disabled", true);
      } else {
        container.removeClass("vacaciones");
        switchElement.prop("disabled", false);

        const valorPrevio = inputElement.data("valor-previo");
        if (valorPrevio) {
          switchElement.prop("checked", true);
          inputElement.prop("disabled", false).val(valorPrevio);
          inputElement.removeData("valor-previo");
        }
        $(".vacaciones-checkbox-sueldoSalario").prop("disabled", false);
      }
      // Actualizar totales
      actualizarTotalAnual();
      calcularAsignacionFamiliar();
      calcularTransporteAlimentacion();
    });

    // Eventos de vacación (Salario)
    $(".vacaciones-checkbox-sueldo").on("change", function () {
      const mes = this.id.replace("_vacaciones_sueldo", "");
      const switchElement = $(`#${mes}_switch_salario`);
      const inputElement = $(`#${mes}_cantidad_salario`);
      const container = $(this).closest(".custom-switch-container");
      let mesVacaciones = "0";

      if (this.checked) {
        container.addClass("vacaciones");
        mesVacaciones = obtenerNumeroMes(mes);
        switchElement.prop("disabled", true);

        if (switchElement.is(":checked")) {
          inputElement.data("valor-previo", inputElement.val());
        }
        switchElement.prop("checked", false).trigger("change");
        inputElement.prop("disabled", true).val("");

        // Deshabilitar los demás checkboxes de vacaciones
        $(".vacaciones-checkbox-sueldo").not(this).prop("disabled", true);
      } else {
        container.removeClass("vacaciones");
        switchElement.prop("disabled", false);

        const valorPrevio = inputElement.data("valor-previo");
        if (valorPrevio) {
          switchElement.prop("checked", true);
          inputElement.prop("disabled", false).val(valorPrevio);
          inputElement.removeData("valor-previo");
        }
        $(".vacaciones-checkbox-sueldo").prop("disabled", false);
      }
      // Actualizar totales
      actualizarTotalAnual_Salarios();
      calcularAsignacionFamiliar_Salarios();
      calcularTransporteAlimentacion_Salarios();
    });

    // Modales - reset al cerrar
    $("#ModalSueldoSalario").on("hidden.bs.modal", function () {
      resetearFormularioSueldo();
    });
    $("#ModalSalario").on("hidden.bs.modal", function () {
      resetearFormularioSalario();
    });

   // Cuando se abre el modal de sueldos
    $("#sueldosModalpresupuesto").on("shown.bs.modal", function () {
      console.log("Modal sueldos abierto, DataTable existe:", $.fn.DataTable.isDataTable("#sueldosTable"));
      // Destruir la tabla si ya existía
      if ($.fn.DataTable.isDataTable("#sueldosTable")) {
          $("#sueldosTable").DataTable().destroy();
          $("#sueldosTable tbody").empty();
      }

      // Inicializar
      console.log("Inicializando tabla sueldos...");
      initPresupuestoSueldos();
    });

   // Cuando se abre el modal de salarios - solo inicializar si no existe
    $("#salariosModalpresupuesto").on("shown.bs.modal", function () {
      console.log("Modal salarios abierto, DataTable existe:", $.fn.DataTable.isDataTable("#salariosTable"));
      if (!$.fn.DataTable.isDataTable("#salariosTable")) {
        console.log("Inicializando tabla salarios...");
        initPresupuestoSalarios();
      }
    });
    // Botón aplicar cantidad masiva (SUELDO)
    $("#aplicar_cantidad_masiva_sueldo").click(function () {
      const cantidad = $("#cantidad_masiva_sueldo").val();
      if (!cantidad || cantidad <= 0) {
        Swal.fire({
          icon: "error",
          title: "Sueldo inválido",
          text: "Por favor, ingrese un sueldo válido mayor a 0",
        });
        return;
      }
      Swal.fire({
        title: "¿Aplicar a todos los meses?",
        text: `Se aplicará el sueldo de S/. ${parseFloat(cantidad).toFixed(
          2
        )} a todos los meses. ¿Desea continuar?`,
        icon: "warning",
        showCancelButton: true,
        confirmButtonColor: "#3085d6",
        cancelButtonColor: "#d33",
        confirmButtonText: "Sí, aplicar",
        cancelButtonText: "Cancelar",
      }).then((result) => {
        if (result.isConfirmed) {
          const meses = [
            "enero",
            "febrero",
            "marzo",
            "abril",
            "mayo",
            "junio",
            "julio",
            "agosto",
            "septiembre",
            "octubre",
            "noviembre",
            "diciembre",
          ];
          meses.forEach((mes) => {
            $(`#${mes}_switch_sueldo`).prop("checked", true);
            $(`#${mes}_cantidad_sueldo`).prop("disabled", false).val(cantidad);
          });
          actualizarTotalAnual();
          calcularAsignacionFamiliar();
          $("#cantidad_masiva_sueldo").val("");
          Swal.fire({
            icon: "success",
            title: "Sueldos aplicados",
            text: "Se han aplicado los sueldos a todos los meses correctamente",
            showConfirmButton: false,
            timer: 1500,
          });
        }
      });
    });

    // Botón aplicar cantidad masiva (SALARIO)
    $("#aplicar_cantidad_masiva_salario").click(function () {
      const cantidad = $("#cantidad_masiva_salario").val();
      if (!cantidad || cantidad <= 0) {
        Swal.fire({
          icon: "error",
          title: "Salario inválido",
          text: "Por favor, ingrese un salario válido mayor a 0",
        });
        return;
      }
      Swal.fire({
        title: "¿Aplicar a todos los meses?",
        text: `Se aplicará el salario de S/. ${parseFloat(cantidad).toFixed(
          2
        )} a todos los meses. ¿Desea continuar?`,
        icon: "warning",
        showCancelButton: true,
        confirmButtonColor: "#3085d6",
        cancelButtonColor: "#d33",
        confirmButtonText: "Sí, aplicar",
        cancelButtonText: "Cancelar",
      }).then((result) => {
        if (result.isConfirmed) {
          const meses = [
            "enero",
            "febrero",
            "marzo",
            "abril",
            "mayo",
            "junio",
            "julio",
            "agosto",
            "septiembre",
            "octubre",
            "noviembre",
            "diciembre",
          ];
          meses.forEach((mes) => {
            $(`#${mes}_switch_salario`).prop("checked", true);
            $(`#${mes}_cantidad_salario`).prop("disabled", false).val(cantidad);
          });
          actualizarTotalAnual_Salarios();
          calcularAsignacionFamiliar_Salarios();
          $("#cantidad_masiva_salario").val("");
          Swal.fire({
            icon: "success",
            title: "Salarios aplicados",
            text: "Se han aplicado los salarios a todos los meses correctamente",
            showConfirmButton: false,
            timer: 1500,
          });
        }
      });
    });

    // 3) Inicializamos las tablas (las cargamos p. ej. si no están en modales)
    initPresupuestoSueldos();
    initPresupuestoSalarios();

    // 4) Forzamos la actualización total en cuanto se termine de cargar el DOM
    setTimeout(function () {
        actualizarTotalSalarios();
        actualizarTotalSueldos();
    }, 500);
  });

  //-------------------------------------------------------------------------------
  //  FUNCIONES AUXILIARES GENERALES
  //-------------------------------------------------------------------------------
  function formatearSoles(monto) {
    const numero = parseFloat(monto || 0);
    const formatoPeruano = numero
      .toFixed(2)
      .replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    const montoFinal = formatoPeruano.replace(/\.(?=[^.]*$)/, ".");
    return "S/ " + montoFinal;
  }

  function obtenerNumeroMes(nombreMes) {
    const meses = {
      enero: "1",
      febrero: "2",
      marzo: "3",
      abril: "4",
      mayo: "5",
      junio: "6",
      julio: "7",
      agosto: "8",
      septiembre: "9",
      octubre: "10",
      noviembre: "11",
      diciembre: "12",
    };
    return meses[nombreMes.toLowerCase()];
  }

  //-------------------------------------------------------------------------------
  //  OBTENER TOTALES (SUELDOS / SALARIOS)
  //-------------------------------------------------------------------------------
  function actualizarTotalSueldos() {
    const year = $('#filtroAnioPresupuesto').val() || 'CAMP' + new Date().getFullYear();

    $.ajax({
      url: "/produccionuva1/produccionuva1_sueldo_mensual_cv/?year=" + year,
      type: "GET",
      dataType: "json",
      success: function (response) {
        const totalAnual = response.data.find(
          (item) => item.Mes === "Total Anual"
        );
        if (totalAnual) {
          const valor = totalAnual.Consolidado_Mes || 0;
          $("#stats_sueldos").text(formatearSoles(valor));
        } else {
          $("#stats_sueldos").text("S/ 0.00");
        }
      },
      error: function () {
        $("#stats_sueldos").text("S/ 0.00");
      },
    });
  }

  function actualizarTotalSalarios() {
    const year = $('#filtroAnioPresupuesto').val() || 'CAMP' + new Date().getFullYear();

    $.ajax({
      url: "/produccionuva1/produccionuva1_salario_mensual_cv/?year=" + year,
      type: "GET",
      dataType: "json",
      success: function (response) {
        const totalAnual = response.data.find(
          (item) => item.Mes === "Total Anual"
        );
        if (totalAnual) {
          const valor = totalAnual.Consolidado_Mes || 0;
          $("#stats_salarios").text(formatearSoles(valor));
        } else {
          $("#stats_salarios").text("S/ 0.00");
        }
      },
      error: function () {
        $("#stats_salarios").text("S/ 0.00");
      },
    });
  }

  //-------------------------------------------------------------------------------
  //  AUTOCOMPLETE DNI (SUELDOS / SALARIOS)
  //-------------------------------------------------------------------------------
  function inicializarAutocompleteDNI() {
    $("#dni_sueldo_salario")
      .on("keypress", function (e) {
        if (e.which === 13) {
          return false;
        }
      })
      .on("input", function () {
        const dni = $(this).val();
        if (dni === "11111111") {
          // Habilitar edición manual
          $("#nombre_sueldo_salario")
            .prop("readonly", false)
            .val("")
            .attr("placeholder", "Ingrese nombre del trabajador");
          $("#regimen_laboral_sueldo_salario")
            .prop("readonly", false)
            .val("")
            .attr("placeholder", "Ingrese régimen laboral");
          $("#cargo_sueldo_salario")
            .prop("readonly", false)
            .val("")
            .attr("placeholder", "Ingrese cargo");
          $("#fecha_ingreso_sueldo_salario")
            .prop("readonly", false)
            .val("")
            .attr("type", "date");
          $(".generic-field-hint").show();
          return;
        } else {
          // Restaurar a solo lectura
          $("#nombre_sueldo_salario")
            .prop("readonly", true)
            .attr("placeholder", "");
          $("#regimen_laboral_sueldo_salario")
            .prop("readonly", true)
            .attr("placeholder", "");
          $("#cargo_sueldo_salario")
            .prop("readonly", true)
            .attr("placeholder", "");
          $("#fecha_ingreso_sueldo_salario")
            .prop("readonly", true)
            .attr("type", "text");
          $(".generic-field-hint").hide();
        }
      })
      .autocomplete({
        source: function (request, response) {
          if (request.term === "11111111") {
            response([]);
            return;
          }
          $.ajax({
            url: "/api_sueldos/",
            dataType: "json",
            data: {
              q: request.term,
            },
            success: function (data) {
              response(data);
            },
            error: function (xhr, status, error) {
              Swal.fire({
                title: "Error!",
                text: "Error al obtener los datos del empleado: " + error,
                icon: "error",
              });
            },
          });
        },
        minLength: 8,
        select: function (event, ui) {
          // Evitar duplicados
          if ($("#dni_sueldo_salario").val() !== "11111111") {
            let dniExistente = false;
            tableSueldos.rows().every(function () {
              if (this.data().dni === ui.item.dni) {
                dniExistente = true;
                return false;
              }
            });
            if (dniExistente) {
              Swal.fire({
                title: "Error!",
                text: "Este DNI ya está registrado en el sistema.",
                icon: "error",
              });
              limpiarCampos();
              return false;
            }
          }
          // Autocompletar
          $("#dni_sueldo_salario").val(ui.item.dni);
          $("#nombre_sueldo_salario").val(ui.item.nombre);
          $("#regimen_laboral_sueldo_salario").val(ui.item.regimen_laboral);
          $("#cargo_sueldo_salario").val(ui.item.cargo);
          $("#fecha_ingreso_sueldo_salario").val(ui.item.fecha_ingreso);
          return false;
        },
      })
      .autocomplete("instance")._renderItem = function (ul, item) {
      return $("<li>")
        .append(
          "<div class='ui-autocomplete-item'>" +
            "DNI: " +
            item.dni +
            "<br>" +
            "Nombre: " +
            item.nombre +
            "<br>" +
            "Cargo: " +
            item.cargo +
            "</div>"
        )
        .appendTo(ul);
    };
  }

  function inicializarAutocompleteDNI_Salario() {
    $("#dni_salario")
      .on("keypress", function (e) {
        if (e.which === 13) {
          return false;
        }
      })
      .on("input", function () {
        const dni = $(this).val();
        if (dni === "11111111") {
          // Habilitar edición manual
          $("#nombre_salario")
            .prop("readonly", false)
            .val("")
            .attr("placeholder", "Ingrese nombre del trabajador");
          $("#regimen_laboral_salario")
            .prop("readonly", false)
            .val("")
            .attr("placeholder", "Ingrese régimen laboral");
          $("#cargo_salario")
            .prop("readonly", false)
            .val("")
            .attr("placeholder", "Ingrese cargo");
          $("#fecha_ingreso_salario")
            .prop("readonly", false)
            .val("")
            .attr("type", "date");
          $(".generic-field-hint").show();
          return;
        } else {
          // Restaurar a solo lectura
          $("#nombre_salario").prop("readonly", true).attr("placeholder", "");
          $("#regimen_laboral_salario")
            .prop("readonly", true)
            .attr("placeholder", "");
          $("#cargo_salario").prop("readonly", true).attr("placeholder", "");
          $("#fecha_ingreso_salario")
            .prop("readonly", true)
            .attr("type", "text");
          $(".generic-field-hint").hide();
        }
      })
      .autocomplete({
        source: function (request, response) {
          if (request.term === "11111111") {
            response([]);
            return;
          }
          $.ajax({
            url: "/api_salarios/",
            dataType: "json",
            data: {
              q: request.term,
            },
            success: function (data) {
              response(data);
            },
            error: function (xhr, status, error) {
              Swal.fire({
                title: "Error!",
                text: "Error al obtener los datos del empleado: " + error,
                icon: "error",
              });
            },
          });
        },
        minLength: 8,
        select: function (event, ui) {
          if ($("#dni_salario").val() !== "11111111") {
            let dniExistente = false;
            tableSalarios.rows().every(function () {
              if (this.data().dni === ui.item.dni) {
                dniExistente = true;
                return false;
              }
            });
            if (dniExistente) {
              Swal.fire({
                title: "Error!",
                text: "Este DNI ya está registrado en el sistema.",
                icon: "error",
              });
              $("#dni_salario").val("");
              $("#nombre_salario").val("");
              $("#regimen_laboral_salario").val("");
              $("#cargo_salario").val("");
              $("#fecha_ingreso_salario").val("");
              return false;
            }
          }
          // Autocompletar
          $("#dni_salario").val(ui.item.dni);
          $("#nombre_salario").val(ui.item.nombre);
          $("#regimen_laboral_salario").val(ui.item.regimen_laboral);
          $("#cargo_salario").val(ui.item.cargo);
          $("#fecha_ingreso_salario").val(ui.item.fecha_ingreso);
          return false;
        },
        change: function (event, ui) {
          if (!ui.item && $("#dni_salario").val() !== "11111111") {
            limpiarCampos();
            Swal.fire({
              title: "Error!",
              text: "Por favor, seleccione un DNI válido.",
              icon: "error",
            });
          }
        },
      })
      .autocomplete("instance")._renderItem = function (ul, item) {
      return $("<li>")
        .append(
          "<div class='ui-autocomplete-item'>" +
            "DNI: " +
            item.dni +
            "<br>" +
            "Nombre: " +
            item.nombre +
            "<br>" +
            "Cargo: " +
            item.cargo +
            "</div>"
        )
        .appendTo(ul);
    };
  }

  function limpiarCampos() {
    $("#dni_sueldo_salario").val("");
    $("#nombre_sueldo_salario").val("");
    $("#regimen_laboral_sueldo_salario").val("");
    $("#cargo_sueldo_salario").val("");
    $("#fecha_ingreso_sueldo_salario").val("");
  }

  //-------------------------------------------------------------------------------
  //  INICIALIZACIÓN DE LA TABLA DE SUELDOS
  //-------------------------------------------------------------------------------
  function obtenerTasaCargaSocial() {
    return $.ajax({
      url: "/configuraciones-sueldos-salarios/",
      type: "GET",
    }).then(function (response) {
      tasaCargaSocialSueldo = response.tasa_carga_social_sueldo;
      sueldoMinimo = parseFloat(response.sueldo_minimo);
      montoTransporte = parseFloat(response.monto_transporte);
      montoAlimentacion = parseFloat(response.monto_alimentacion);
    });
  }

  function actualizarFooterSueldos() {

    const year = $('#filtroAnioPresupuesto').val() || 'CAMP' + new Date().getFullYear();

    $.ajax({
      url: "/produccionuva1/produccionuva1_sueldo_mensual_cv/?year=" + year,
      type: "GET",
      success: function (response) {

        if (!response.data) return;

        const consolidadosPorMes = {};
        let totalAnual = 0;

        response.data.forEach((item) => {

          if (item.Mes !== "Total Anual") {
            consolidadosPorMes[item.Mes.toLowerCase()] = item.Consolidado_Mes;
          } else {
            totalAnual = item.Consolidado_Mes;
          }

        });

        const footer = $(tableSueldos.table().footer());

        Object.keys(consolidadosPorMes).forEach((mes) => {

          footer
            .find(`th[data-mes="${mes}"]`)
            .html(formatearMonto(consolidadosPorMes[mes] || 0));

        });

        footer
          .find('th[data-total="general"]')
          .html(formatearMonto(totalAnual));

      }
    });

  }

  // Función auxiliar para formatear montos
  function formatearMonto(monto) {
    return (
      "S/. " +
      parseFloat(monto)
        .toFixed(2)
        .replace(/\d(?=(\d{3})+\.)/g, "$&,")
    );
  }



  var CAMPANIA_ACTIVA = null;
  function initPresupuestoSueldos() {
    obtenerTasaCargaSocial().then(function () {
      // var yearVal = $('#filtroAnioPresupuesto').val() || 'CAMP' + new Date().getFullYear();
      CAMPANIA_ACTIVA = $('#filtroAnioPresupuesto').val();

      if (!CAMPANIA_ACTIVA) {
        CAMPANIA_ACTIVA = 'CAMP' + new Date().getFullYear();
      }
      tableSueldos = $("#sueldosTable").DataTable({
        dom: "Bfrtip",
        buttons: [
          {
            text: '<i class="fas fa-sync-alt"></i>',
            className: "btn-sm btn-secondary",
            action: function (e, dt, node, config) {
              // Añadir animación de giro
              $(node).find("i").addClass("fa-spin");
              
              // Obtener año actual del filtro
              var currentYear = $('#filtroAnioPresupuesto').val() || 'CAMP' + new Date().getFullYear();

              // Recargar la tabla con el año correcto
              dt.ajax.url("/produccionuva1/produccionuva1_sueldos_cv/?year=" + currentYear).load(function () {
                // Callback después de la recarga
                setTimeout(() => {
                  $(node).find("i").removeClass("fa-spin");
                }, 1000);

                // Actualizar totales
                actualizarTotalSueldos();
                actualizarFooterSueldos();
              });
            },
          },
          {
            extend: "excelHtml5",
            title: "PRESUPUESTO_SUELDOS",
            text: '<i class="far fa-file-excel"></i> Excel',
            className: "btn-sm btn-success",
            customize: function (xlsx) {
              var sheet = xlsx.xl.worksheets["sheet1.xml"];
              $("row:first c", sheet).attr("s", "2"); // Estilo para encabezados
            },
            excelStyles: {
              template: [
                {
                  id: "2",
                  font: {
                    bold: true,
                    color: "FFFFFF",
                  },
                  fill: {
                    pattern: {
                      bgColor: "2E8B57",
                    },
                  },
                },
              ],
            },
            exportOptions: {
              columns: [
                0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17,
                18, 19,
              ],
              format: {
                body: function (data, row, column) {
                  if (data === null || data === undefined) return "0";

                  // Crear un elemento temporal para remover HTML
                  const temp = document.createElement("div");
                  temp.innerHTML = data;
                  data = temp.textContent || temp.innerText;
                  data = data.trim();

                  // Extraer solo el valor numérico del sueldo (sin la carga social)
                  if (data.includes("S/")) {
                    const valores = data.match(/\d+(\.\d+)?/g);
                    if (valores && valores.length > 0) {
                      return valores[0]; // Retorna solo el primer número encontrado
                    }
                  }

                  if (data.includes("VACACIONES")) {
                    return "0";
                  }

                  return data;
                },
              },
            },
          },
          {
            extend: "pdfHtml5",
            title: "RPT_PRESUPUESTO_SUELDOS",
            text: '<i class="far fa-file-pdf"></i> PDF',
            className: "btn-sm btn-danger",
            orientation: "landscape",
            pageSize: "A4",
            customize: function (doc) {
              // Reducir el tamaño de la fuente
              doc.defaultStyle.fontSize = 6;
              doc.styles.tableHeader.fontSize = 7;
              doc.styles.title.fontSize = 12;

              // Ajustar el ancho de las columnas
              var table = doc.content[1].table.body;
              var colCount = table[0].length;
              var widths = [];
              for (var i = 0; i < colCount; i++) {
                widths.push("*");
              }
              doc.content[1].table.widths = widths;

              // Reducir márgenes
              doc.pageMargins = [10, 10, 10, 10];

              // Ajustar el contenido para que quepa en una página
              doc.content[1].table.keepWithHeaderRows = 1;
              doc.content[1].table.body.forEach(function (row) {
                row.forEach(function (cell) {
                  cell.alignment = "left";
                });
              });
            },
            exportOptions: {
              columns: [
                0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17,
                18, 19,
              ], // Excluir la columna de acciones
              format: {
                body: function (data, row, column, node) {
                  // Acortar texto largo si es necesario
                  return data.length > 20 ? data.substr(0, 20) + "..." : data;
                },
              },
            },
          },
          {
            text: '<i class="fas fa-plus mr-1"></i>AGREGAR',
            className: "btn-sm btn-success btn-agregar",
            action: function (e, dt, node, config) {
              $("#ModalSueldoSalario").modal("show");
            },
          },
        ],

        scrollX: true,
        scrollY: 250,
        scrollCollapse: true,
        searching: false,
        pageLength: 7,
        ordering: true,
        order: [[0, "desc"]],

        language: {
          url: dataTableEsUrl,
        },
        ajax: {
          url: "/produccionuva1/produccionuva1_sueldos_cv/?year=" + ($('#filtroAnioPresupuesto').val() || 'CAMP' + new Date().getFullYear()),
          dataSrc: "data",
        },
        columns: [
          { data: "id", title: "ID", visible: false },
          {
            data: null,
            title: "N°",
            className: "text-center",
            render: function (data, type, row, meta) {
              // Simplemente usar el índice de la fila + 1
              return meta.row + 1;
            },
          },
          { data: "dni" },
          { data: "nombre" },
          { data: "regimen_laboral" },
          { data: "cargo" },
          { data: "fecha_ingreso" },
          {
            data: "enero",
            render: function (data, type, row) {
              const sueldo = parseFloat(data) || 0;
              let cargaSocial;

              const mesVacaciones = String(row.vacacion).trim();
              const isVacaciones = mesVacaciones === "1";

              if (isVacaciones) {
                let sueldoReferencia = parseFloat(row.febrero) || 0;

                if (row.asignacion === "1") {
                  cargaSocial =
                    (sueldoReferencia + 0.1 * sueldoMinimo) *
                    tasaCargaSocialSueldo;
                } else {
                  cargaSocial = sueldoReferencia * tasaCargaSocialSueldo;
                }

                return `<span class="text-info fw-bold" style="font-size: 1.1em; letter-spacing: 0.5px; font-weight: bold;">
                                <i class="fas fa-umbrella-beach me-1"></i> VACACIONES
                            </span>
                            <br>
                            <span class="badge badge-secondary text-dark">
                                S/ ${cargaSocial.toFixed(2)}
                            </span>`;
              } else {
                if (row.asignacion === "1") {
                  cargaSocial =
                    (sueldo + 0.1 * sueldoMinimo) * tasaCargaSocialSueldo;
                } else {
                  cargaSocial = sueldo * tasaCargaSocialSueldo;
                }

                return `S/ ${sueldo.toFixed(2)}
                            <br>
                            <span class="badge badge-secondary text-dark">
                                S/ ${cargaSocial.toFixed(2)}
                            </span>`;
              }
            },
          },
          {
            data: "febrero",
            render: function (data, type, row) {
              const sueldo = parseFloat(data) || 0;
              let cargaSocial;

              const mesVacaciones = String(row.vacacion).trim();
              const isVacaciones = mesVacaciones === "2";

              // Si no hay sueldo y no hay vacaciones, retornar carga social 0
              if (sueldo === 0 && (mesVacaciones === "0" || !mesVacaciones)) {
                return `S/ 0.00
                          <br>
                          <span class="badge badge-secondary text-dark">
                              S/ 0.00
                          </span>`;
              }

              if (isVacaciones) {
                let sueldoReferencia =
                  parseFloat(row.enero) || parseFloat(row.marzo) || 0;

                if (sueldoReferencia === 0) {
                  sueldoReferencia = parseFloat(row.marzo) || 0;
                }

                if (row.asignacion === "1") {
                  cargaSocial =
                    (sueldoReferencia + 0.1 * sueldoMinimo) *
                    tasaCargaSocialSueldo;
                } else {
                  cargaSocial = sueldoReferencia * tasaCargaSocialSueldo;
                }

                return `<span class="text-info fw-bold" style="font-size: 1.1em; letter-spacing: 0.5px; font-weight: bold;">
                                <i class="fas fa-umbrella-beach me-1"></i> VACACIONES
                            </span>
                            <br>
                            <span class="badge badge-secondary text-dark">
                                S/ ${cargaSocial.toFixed(2)}
                            </span>`;
              } else {
                if (row.asignacion === "1") {
                  cargaSocial =
                    (sueldo + 0.1 * sueldoMinimo) * tasaCargaSocialSueldo;
                } else {
                  cargaSocial = sueldo * tasaCargaSocialSueldo;
                }

                return `S/ ${sueldo.toFixed(2)}
                            <br>
                            <span class="badge badge-secondary text-dark">
                                S/ ${cargaSocial.toFixed(2)}
                            </span>`;
              }
            },
          },
          {
            data: "marzo",
            render: function (data, type, row) {
              const sueldo = parseFloat(data) || 0;
              let cargaSocial = 0;

              const mesVacaciones = String(row.vacacion).trim();
              const isVacaciones = mesVacaciones === "3";

              // Si no hay sueldo y no hay vacaciones, retornar carga social 0
              if (sueldo === 0 && (mesVacaciones === "0" || !mesVacaciones)) {
                return `S/ 0.00
                          <br>
                          <span class="badge badge-secondary text-dark">
                              S/ 0.00
                          </span>`;
              }

              if (isVacaciones) {
                let sueldoReferencia =
                  parseFloat(row.febrero) || parseFloat(row.abril) || 0;

                if (sueldoReferencia === 0) {
                  sueldoReferencia = parseFloat(row.abril) || 0;
                }

                if (row.asignacion === "1") {
                  cargaSocial =
                    (sueldoReferencia + 0.1 * sueldoMinimo) *
                    tasaCargaSocialSueldo;
                } else {
                  cargaSocial = sueldoReferencia * tasaCargaSocialSueldo;
                }

                return `<span class="text-info fw-bold" style="font-size: 1.1em; letter-spacing: 0.5px; font-weight: bold;">
                                <i class="fas fa-umbrella-beach me-1"></i> VACACIONES
                            </span>
                            <br>
                            <span class="badge badge-secondary text-dark">
                                S/ ${cargaSocial.toFixed(2)}
                            </span>`;
              } else {
                if (row.asignacion === "1") {
                  cargaSocial =
                    (sueldo + 0.1 * sueldoMinimo) * tasaCargaSocialSueldo;
                } else {
                  cargaSocial = sueldo * tasaCargaSocialSueldo;
                }

                return `S/ ${sueldo.toFixed(2)}
                            <br>
                            <span class="badge badge-secondary text-dark">
                                S/ ${cargaSocial.toFixed(2)}
                            </span>`;
              }
            },
          },
          {
            data: "abril",
            render: function (data, type, row) {
              const sueldo = parseFloat(data) || 0;
              let cargaSocial;

              const mesVacaciones = String(row.vacacion).trim();
              const isVacaciones = mesVacaciones === "4";

              // Si no hay sueldo y no hay vacaciones, retornar carga social 0
              if (sueldo === 0 && (mesVacaciones === "0" || !mesVacaciones)) {
                return `S/ 0.00
                          <br>
                          <span class="badge badge-secondary text-dark">
                              S/ 0.00
                          </span>`;
              }

              // Si no hay sueldo y no hay vacaciones, retornar carga social 0
              if (sueldo === 0 && (mesVacaciones === "0" || !mesVacaciones)) {
                return `S/ 0.00
                          <br>
                          <span class="badge badge-secondary text-dark">
                              S/ 0.00
                          </span>`;
              }

              if (isVacaciones) {
                let sueldoReferencia =
                  parseFloat(row.marzo) || parseFloat(row.mayo) || 0;

                if (sueldoReferencia === 0) {
                  sueldoReferencia = parseFloat(row.mayo) || 0;
                }

                if (row.asignacion === "1") {
                  cargaSocial =
                    (sueldoReferencia + 0.1 * sueldoMinimo) *
                    tasaCargaSocialSueldo;
                } else {
                  cargaSocial = sueldoReferencia * tasaCargaSocialSueldo;
                }

                return `<span class="text-info fw-bold" style="font-size: 1.1em; letter-spacing: 0.5px; font-weight: bold;">
                                <i class="fas fa-umbrella-beach me-1"></i> VACACIONES
                            </span>
                            <br>
                            <span class="badge badge-secondary text-dark">
                                S/ ${cargaSocial.toFixed(2)}
                            </span>`;
              } else {
                if (row.asignacion === "1") {
                  cargaSocial =
                    (sueldo + 0.1 * sueldoMinimo) * tasaCargaSocialSueldo;
                } else {
                  cargaSocial = sueldo * tasaCargaSocialSueldo;
                }

                return `S/ ${sueldo.toFixed(2)}
                            <br>
                            <span class="badge badge-secondary text-dark">
                                S/ ${cargaSocial.toFixed(2)}
                            </span>`;
              }
            },
          },
          {
            data: "mayo",
            render: function (data, type, row) {
              const sueldo = parseFloat(data) || 0;
              let cargaSocial;

              const mesVacaciones = String(row.vacacion).trim();
              const isVacaciones = mesVacaciones === "5";

              // Si no hay sueldo y no hay vacaciones, retornar carga social 0
              if (sueldo === 0 && (mesVacaciones === "0" || !mesVacaciones)) {
                return `S/ 0.00
                          <br>
                          <span class="badge badge-secondary text-dark">
                              S/ 0.00
                          </span>`;
              }

              if (isVacaciones) {
                let sueldoReferencia =
                  parseFloat(row.abril) || parseFloat(row.junio) || 0;

                if (sueldoReferencia === 0) {
                  sueldoReferencia = parseFloat(row.junio) || 0;
                }

                if (row.asignacion === "1") {
                  cargaSocial =
                    (sueldoReferencia + 0.1 * sueldoMinimo) *
                    tasaCargaSocialSueldo;
                } else {
                  cargaSocial = sueldoReferencia * tasaCargaSocialSueldo;
                }

                return `<span class="text-info fw-bold" style="font-size: 1.1em; letter-spacing: 0.5px; font-weight: bold;">
                                <i class="fas fa-umbrella-beach me-1"></i> VACACIONES
                            </span>
                            <br>
                            <span class="badge badge-secondary text-dark">
                                S/ ${cargaSocial.toFixed(2)}
                            </span>`;
              } else {
                if (row.asignacion === "1") {
                  cargaSocial =
                    (sueldo + 0.1 * sueldoMinimo) * tasaCargaSocialSueldo;
                } else {
                  cargaSocial = sueldo * tasaCargaSocialSueldo;
                }

                return `S/ ${sueldo.toFixed(2)}
                            <br>
                            <span class="badge badge-secondary text-dark">
                                S/ ${cargaSocial.toFixed(2)}
                            </span>`;
              }
            },
          },
          {
            data: "junio",
            render: function (data, type, row) {
              const sueldo = parseFloat(data) || 0;
              let cargaSocial;

              const mesVacaciones = String(row.vacacion).trim();
              const isVacaciones = mesVacaciones === "6";

              // Si no hay sueldo y no hay vacaciones, retornar carga social 0
              if (sueldo === 0 && (mesVacaciones === "0" || !mesVacaciones)) {
                return `S/ 0.00
                          <br>
                          <span class="badge badge-secondary text-dark">
                              S/ 0.00
                          </span>`;
              }

              if (isVacaciones) {
                let sueldoReferencia =
                  parseFloat(row.mayo) || parseFloat(row.julio) || 0;

                if (sueldoReferencia === 0) {
                  sueldoReferencia = parseFloat(row.julio) || 0;
                }

                if (row.asignacion === "1") {
                  cargaSocial =
                    (sueldoReferencia + 0.1 * sueldoMinimo) *
                    tasaCargaSocialSueldo;
                } else {
                  cargaSocial = sueldoReferencia * tasaCargaSocialSueldo;
                }

                return `<span class="text-info fw-bold" style="font-size: 1.1em; letter-spacing: 0.5px; font-weight: bold;">
                                <i class="fas fa-umbrella-beach me-1"></i> VACACIONES
                            </span>
                            <br>
                            <span class="badge badge-secondary text-dark">
                                S/ ${cargaSocial.toFixed(2)}
                            </span>`;
              } else {
                if (row.asignacion === "1") {
                  cargaSocial =
                    (sueldo + 0.1 * sueldoMinimo) * tasaCargaSocialSueldo;
                } else {
                  cargaSocial = sueldo * tasaCargaSocialSueldo;
                }

                return `S/ ${sueldo.toFixed(2)}
                            <br>
                            <span class="badge badge-secondary text-dark">
                                S/ ${cargaSocial.toFixed(2)}
                            </span>`;
              }
            },
          },
          {
            data: "julio",
            render: function (data, type, row) {
              const sueldo = parseFloat(data) || 0;
              let cargaSocial;

              const mesVacaciones = String(row.vacacion).trim();
              const isVacaciones = mesVacaciones === "7";

              // Si no hay sueldo y no hay vacaciones, retornar carga social 0
              if (sueldo === 0 && (mesVacaciones === "0" || !mesVacaciones)) {
                return `S/ 0.00
                          <br>
                          <span class="badge badge-secondary text-dark">
                              S/ 0.00
                          </span>`;
              }

              if (isVacaciones) {
                let sueldoReferencia =
                  parseFloat(row.junio) || parseFloat(row.agosto) || 0;

                if (sueldoReferencia === 0) {
                  sueldoReferencia = parseFloat(row.agosto) || 0;
                }

                if (row.asignacion === "1") {
                  cargaSocial =
                    (sueldoReferencia + 0.1 * sueldoMinimo) *
                    tasaCargaSocialSueldo;
                } else {
                  cargaSocial = sueldoReferencia * tasaCargaSocialSueldo;
                }

                return `<span class="text-info fw-bold" style="font-size: 1.1em; letter-spacing: 0.5px; font-weight: bold;">
                                <i class="fas fa-umbrella-beach me-1"></i> VACACIONES
                            </span>
                            <br>
                            <span class="badge badge-secondary text-dark">
                                S/ ${cargaSocial.toFixed(2)}
                            </span>`;
              } else {
                if (row.asignacion === "1") {
                  cargaSocial =
                    (sueldo + 0.1 * sueldoMinimo) * tasaCargaSocialSueldo;
                } else {
                  cargaSocial = sueldo * tasaCargaSocialSueldo;
                }

                return `S/ ${sueldo.toFixed(2)}
                            <br>
                            <span class="badge badge-secondary text-dark">
                                S/ ${cargaSocial.toFixed(2)}
                            </span>`;
              }
            },
          },
          {
            data: "agosto",
            render: function (data, type, row) {
              const sueldo = parseFloat(data) || 0;
              let cargaSocial;

              const mesVacaciones = String(row.vacacion).trim();
              const isVacaciones = mesVacaciones === "8";

              // Si no hay sueldo y no hay vacaciones, retornar carga social 0
              if (sueldo === 0 && (mesVacaciones === "0" || !mesVacaciones)) {
                return `S/ 0.00
                          <br>
                          <span class="badge badge-secondary text-dark">
                              S/ 0.00
                          </span>`;
              }

              if (isVacaciones) {
                let sueldoReferencia =
                  parseFloat(row.julio) || parseFloat(row.septiembre) || 0;

                if (sueldoReferencia === 0) {
                  sueldoReferencia = parseFloat(row.septiembre) || 0;
                }

                if (row.asignacion === "1") {
                  cargaSocial =
                    (sueldoReferencia + 0.1 * sueldoMinimo) *
                    tasaCargaSocialSueldo;
                } else {
                  cargaSocial = sueldoReferencia * tasaCargaSocialSueldo;
                }

                return `<span class="text-info fw-bold" style="font-size: 1.1em; letter-spacing: 0.5px; font-weight: bold;">
                                <i class="fas fa-umbrella-beach me-1"></i> VACACIONES
                            </span>
                            <br>
                            <span class="badge badge-secondary text-dark">
                                S/ ${cargaSocial.toFixed(2)}
                            </span>`;
              } else {
                if (row.asignacion === "1") {
                  cargaSocial =
                    (sueldo + 0.1 * sueldoMinimo) * tasaCargaSocialSueldo;
                } else {
                  cargaSocial = sueldo * tasaCargaSocialSueldo;
                }

                return `S/ ${sueldo.toFixed(2)}
                            <br>
                            <span class="badge badge-secondary text-dark">
                                S/ ${cargaSocial.toFixed(2)}
                            </span>`;
              }
            },
          },
          {
            data: "septiembre",
            render: function (data, type, row) {
              const sueldo = parseFloat(data) || 0;
              let cargaSocial;

              const mesVacaciones = String(row.vacacion).trim();
              const isVacaciones = mesVacaciones === "9";

              // Si no hay sueldo y no hay vacaciones, retornar carga social 0
              if (sueldo === 0 && (mesVacaciones == "0" || !mesVacaciones)) {
                return `S/ 0.00
                          <br>
                          <span class="badge badge-secondary text-dark">
                              S/ 0.00
                          </span>`;
              }

              if (isVacaciones) {
                let sueldoReferencia =
                  parseFloat(row.agosto) || parseFloat(row.octubre) || 0;

                if (sueldoReferencia === 0) {
                  sueldoReferencia = parseFloat(row.octubre) || 0;
                }

                if (row.asignacion === "1") {
                  cargaSocial =
                    (sueldoReferencia + 0.1 * sueldoMinimo) *
                    tasaCargaSocialSueldo;
                } else {
                  cargaSocial = sueldoReferencia * tasaCargaSocialSueldo;
                }

                return `<span class="text-info fw-bold" style="font-size: 1.1em; letter-spacing: 0.5px; font-weight: bold;">
                                <i class="fas fa-umbrella-beach me-1"></i> VACACIONES
                            </span>
                            <br>
                            <span class="badge badge-secondary text-dark">
                                S/ ${cargaSocial.toFixed(2)}
                            </span>`;
              } else {
                if (row.asignacion === "1") {
                  cargaSocial =
                    (sueldo + 0.1 * sueldoMinimo) * tasaCargaSocialSueldo;
                } else {
                  cargaSocial = sueldo * tasaCargaSocialSueldo;
                }

                return `S/ ${sueldo.toFixed(2)}
                            <br>
                            <span class="badge badge-secondary text-dark">
                                S/ ${cargaSocial.toFixed(2)}
                            </span>`;
              }
            },
          },
          {
            data: "octubre",
            render: function (data, type, row) {
              const sueldo = parseFloat(data) || 0;
              let cargaSocial;

              const mesVacaciones = String(row.vacacion).trim();
              const isVacaciones = mesVacaciones === "10";

              // Si no hay sueldo y no hay vacaciones, retornar carga social 0
              if (sueldo === 0 && (mesVacaciones === "0" || !mesVacaciones)) {
                return `S/ 0.00
                          <br>
                          <span class="badge badge-secondary text-dark">
                              S/ 0.00
                          </span>`;
              }

              if (isVacaciones) {
                let sueldoReferencia =
                  parseFloat(row.septiembre) || parseFloat(row.noviembre) || 0;

                if (sueldoReferencia === 0) {
                  sueldoReferencia = parseFloat(row.noviembre) || 0;
                }

                if (row.asignacion === "1") {
                  cargaSocial =
                    (sueldoReferencia + 0.1 * sueldoMinimo) *
                    tasaCargaSocialSueldo;
                } else {
                  cargaSocial = sueldoReferencia * tasaCargaSocialSueldo;
                }

                return `<span class="text-info fw-bold" style="font-size: 1.1em; letter-spacing: 0.5px; font-weight: bold;">
                                <i class="fas fa-umbrella-beach me-1"></i> VACACIONES
                            </span>
                            <br>
                            <span class="badge badge-secondary text-dark">
                                S/ ${cargaSocial.toFixed(2)}
                            </span>`;
              } else {
                if (row.asignacion === "1") {
                  cargaSocial =
                    (sueldo + 0.1 * sueldoMinimo) * tasaCargaSocialSueldo;
                } else {
                  cargaSocial = sueldo * tasaCargaSocialSueldo;
                }

                return `S/ ${sueldo.toFixed(2)}
                            <br>
                            <span class="badge badge-secondary text-dark">
                                S/ ${cargaSocial.toFixed(2)}
                            </span>`;
              }
            },
          },
          {
            data: "noviembre",
            render: function (data, type, row) {
              const sueldo = parseFloat(data) || 0;
              let cargaSocial;

              const mesVacaciones = String(row.vacacion).trim();
              const isVacaciones = mesVacaciones === "11";

              // Si no hay sueldo y no hay vacaciones, retornar carga social 0
              if (sueldo === 0 && (mesVacaciones === "0" || !mesVacaciones)) {
                return `S/ 0.00
                          <br>
                          <span class="badge badge-secondary text-dark">
                              S/ 0.00
                          </span>`;
              }

              if (isVacaciones) {
                let sueldoReferencia =
                  parseFloat(row.octubre) || parseFloat(row.diciembre) || 0;

                if (sueldoReferencia === 0) {
                  sueldoReferencia = parseFloat(row.diciembre) || 0;
                }

                if (row.asignacion === "1") {
                  cargaSocial =
                    (sueldoReferencia + 0.1 * sueldoMinimo) *
                    tasaCargaSocialSueldo;
                } else {
                  cargaSocial = sueldoReferencia * tasaCargaSocialSueldo;
                }

                return `<span class="text-info fw-bold" style="font-size: 1.1em; letter-spacing: 0.5px; font-weight: bold;">
                                <i class="fas fa-umbrella-beach me-1"></i> VACACIONES
                            </span>
                            <br>
                            <span class="badge badge-secondary text-dark">
                                S/ ${cargaSocial.toFixed(2)}
                            </span>`;
              } else {
                if (row.asignacion === "1") {
                  cargaSocial =
                    (sueldo + 0.1 * sueldoMinimo) * tasaCargaSocialSueldo;
                } else {
                  cargaSocial = sueldo * tasaCargaSocialSueldo;
                }

                return `S/ ${sueldo.toFixed(2)}
                            <br>
                            <span class="badge badge-secondary text-dark">
                                S/ ${cargaSocial.toFixed(2)}
                            </span>`;
              }
            },
          },
          {
            data: "diciembre",
            render: function (data, type, row) {
              const sueldo = parseFloat(data) || 0;
              let cargaSocial;

              const mesVacaciones = String(row.vacacion).trim();
              const isVacaciones = mesVacaciones === "12";

              // Si no hay sueldo y no hay vacaciones, retornar carga social 0
              if (sueldo === 0 && (mesVacaciones === "0" || !mesVacaciones)) {
                return `S/ 0.00
                          <br>
                          <span class="badge badge-secondary text-dark">
                              S/ 0.00
                          </span>`;
              }

              if (isVacaciones) {
                let sueldoReferencia =
                  parseFloat(row.noviembre) || parseFloat(row.enero) || 0;

                if (sueldoReferencia === 0) {
                  sueldoReferencia = parseFloat(row.enero) || 0;
                }

                if (row.asignacion === "1") {
                  cargaSocial =
                    (sueldoReferencia + 0.1 * sueldoMinimo) *
                    tasaCargaSocialSueldo;
                } else {
                  cargaSocial = sueldoReferencia * tasaCargaSocialSueldo;
                }

                return `<span class="text-info fw-bold" style="font-size: 1.1em; letter-spacing: 0.5px; font-weight: bold;">
                                <i class="fas fa-umbrella-beach me-1"></i> VACACIONES
                            </span>
                            <br>
                            <span class="badge badge-secondary text-dark">
                                S/ ${cargaSocial.toFixed(2)}
                            </span>`;
              } else {
                if (row.asignacion === "1") {
                  cargaSocial =
                    (sueldo + 0.1 * sueldoMinimo) * tasaCargaSocialSueldo;
                } else {
                  cargaSocial = sueldo * tasaCargaSocialSueldo;
                }

                return `S/ ${sueldo.toFixed(2)}
                            <br>
                            <span class="badge badge-secondary text-dark">
                                S/ ${cargaSocial.toFixed(2)}
                            </span>`;
              }
            },
          },

          {
            data: null,
            title: "Total Anual",
            render: function (data, type, row) {
              let totalSueldo = 0;
              let totalCargaSocial = 0;
              let totalTransporte = 0;
              let totalAlimentacion = 0;
              const mesVacaciones = String(row.vacacion).trim();

              // Sumar los valores de todos los meses
              [
                "enero",
                "febrero",
                "marzo",
                "abril",
                "mayo",
                "junio",
                "julio",
                "agosto",
                "septiembre",
                "octubre",
                "noviembre",
                "diciembre",
              ].forEach((mes, index) => {
                const mesActual = String(index + 1);
                const sueldo = parseFloat(row[mes]) || 0;

                if (mesVacaciones === mesActual) {
                  // En mes de vacaciones, calcular carga social con sueldo de referencia
                  let sueldoReferencia;
                  if (index === 0) {
                    // Si es enero, usar febrero como referencia
                    sueldoReferencia = parseFloat(row["febrero"]) || 0;
                  } else {
                    // Usar mes anterior como referencia
                    const mesAnterior = [
                      "enero",
                      "febrero",
                      "marzo",
                      "abril",
                      "mayo",
                      "junio",
                      "julio",
                      "agosto",
                      "septiembre",
                      "octubre",
                      "noviembre",
                      "diciembre",
                    ][index - 1];
                    sueldoReferencia = parseFloat(row[mesAnterior]) || 0;
                  }

                  // Calcular carga social con sueldo de referencia
                  if (row.asignacion === "1") {
                    totalCargaSocial +=
                      (sueldoReferencia + 0.1 * sueldoMinimo) *
                      tasaCargaSocialSueldo;
                  } else {
                    totalCargaSocial +=
                      sueldoReferencia * tasaCargaSocialSueldo;
                  }
                } else {
                  // Mes normal
                  if (sueldo > 0) {
                    totalSueldo += sueldo;
                    // Calcular carga social normal
                    if (row.asignacion === "1") {
                      totalCargaSocial +=
                        (sueldo + 0.1 * sueldoMinimo) * tasaCargaSocialSueldo;
                    } else {
                      totalCargaSocial += sueldo * tasaCargaSocialSueldo;
                    }
                    // Calcular transporte y alimentación
                    totalTransporte += montoTransporte * 26;
                    totalAlimentacion += montoAlimentacion * 26;
                  }
                }
              });

              return `
                    <div class="d-flex flex-column" style="gap: 3px;">
                        <!-- Sueldo Base -->
                        <div class="text-right" style="font-weight: bold;">
                            S/ ${totalSueldo.toFixed(2)}
                        </div>
                        
                        <!-- Primera fila: Carga Social y Transporte -->
                        <div class="d-flex justify-content-end" style="gap: 5px;">
                            <span class="badge badge-secondary text-dark" 
                                  style="min-width: 85px; font-size: 11px;" 
                                  title="Carga Social">
                                <i class="fas fa-money"></i>
                                S/ ${totalCargaSocial.toFixed(2)}
                            </span>
                            
                            <span class="badge badge-info text-dark" 
                                  style="min-width: 85px; font-size: 11px;" 
                                  title="Transporte">
                                <i class="fas fa-bus"></i>
                                S/ ${totalTransporte.toFixed(2)}
                            </span>
                        </div>
                        
                        <!-- Segunda fila: Alimentación y Asignación Familiar -->
                        <div class="d-flex justify-content-end" style="gap: 5px;">
                            <span class="badge badge-warning text-dark" 
                                  style="min-width: 85px; font-size: 11px;" 
                                  title="Alimentación">
                                <i class="fas fa-utensils"></i>
                                S/ ${totalAlimentacion.toFixed(2)}
                            </span>
                            
                            ${
                              row.asignacion === "1"
                                ? `<span class="badge badge-success text-dark" 
                                        style="min-width: 85px; font-size: 11px; background-color: #bfff00;" 
                                        title="Asignación Familiar">
                                        <i class="fas fa-users"></i>
                                        S/ ${(0.1 * sueldoMinimo * 12).toFixed(
                                          2
                                        )}
                                    </span>`
                                : `<span style="min-width: 85px;"></span>`
                            }
                        </div>
                    </div>
                `;
            },
          },

          {
            data: null,
            title: "Acciones",
            className: "sticky-col",
            render: function (data, type, row) {
              return (
                '<div class="d-flex justify-content-around">' +
                '<button class="btn  btn-danger delete-btn " data-id="' +
                row.id +
                '" title="Eliminar">' +
                '<i class="fas fa-trash fa-sm"></i>' +
                "</button>" +
                '<button class="btn  btn-primary edit-btn " data-id="' +
                row.id +
                '" title="Editar">' +
                '<i class="fas fa-edit fa-sm"></i>' +
                "</button>" +
                "</div>"
              );
            },
            orderable: false,
          },
        ],

        columnDefs: [
          {
            targets: [0, 1, 2, 3, 4, 5],
            className: "dt-body-left fw-bold",
            width: "150px",
          },
          {
            targets: "_all",
            className: "dt-body-right fw-bold",
            width: "120px",
          },
        ],

        responsive: true,
        ordering: true,
        order: [[0, "desc"]],
        language: {
          url: dataTableEsUrl,
        },

      });

      tableSueldos.on('xhr', function () {
        actualizarFooterSueldos();
      });
      
    });

    actualizarTotalSueldos();

    // Evento para eliminar
    $("#sueldosTable tbody").on("click", ".delete-btn", function () {
      var id = $(this).data("id");
      eliminarSueldo(id);
    });

    // Evento para editar
    $("#sueldosTable tbody").on("click", ".edit-btn", function () {
      var id = $(this).data("id");
      editarSueldo(id);
    });

    // Manejo del formulario

    $("#formSueldoSalario")
      .off("submit")
      .on("submit", function (e) {
        e.preventDefault();

        // Prevenir múltiples envíos
        const $form = $(this);
        const $submitButton = $form.find('button[type="submit"]');

        // Si el formulario ya está siendo enviado, detener
        if ($form.data("submitting")) {
          return false;
        }

        // Marcar el formulario como en proceso de envío
        $form.data("submitting", true);
        $submitButton.prop("disabled", true);

        // Verificar si al menos un mes tiene sueldo asignado
        let tieneMesesAsignados = false;
        let mesVacaciones = "0"; // Valor por defecto

        // Obtener el mes de vacaciones seleccionado
        $(".vacaciones-checkbox-sueldoSalario").each(function () {
          if ($(this).is(":checked")) {
            const mes = this.id.replace("_vacaciones_sueldoSalario", "");
            mesVacaciones = obtenerNumeroMes(mes);
          }
        });

        // Verificar meses con sueldo asignado
        [
          "enero",
          "febrero",
          "marzo",
          "abril",
          "mayo",
          "junio",
          "julio",
          "agosto",
          "septiembre",
          "octubre",
          "noviembre",
          "diciembre",
        ].forEach(function (mes) {
          if (
            $(`#${mes}_switch_sueldo`).is(":checked") &&
            parseFloat($(`#${mes}_cantidad_sueldo`).val()) > 0
          ) {
            tieneMesesAsignados = true;
          }
        });

        if (!tieneMesesAsignados) {
          Swal.fire({
            title: "Error!",
            text: "Debe asignar sueldo a al menos un mes",
            icon: "error",
          });
          // Restaurar el formulario para permitir nuevo intento
          $form.data("submitting", false);
          $submitButton.prop("disabled", false);
          return false;
        }

        // Obtener el ID si es una actualización
        var formId = $(this).attr("data-id");
        var isUpdate = formId !== undefined;

        // Construir el objeto de datos
        var jsonData = {
          dni: $("#dni_sueldo_salario").val(),
          nombre: $("#nombre_sueldo_salario").val(),
          regimen_laboral: $("#regimen_laboral_sueldo_salario").val(),
          cargo: $("#cargo_sueldo_salario").val(),
          fecha_ingreso: $("#fecha_ingreso_sueldo_salario").val(),
          asignacion: $("#check_asignacion_familiar").is(":checked")
            ? "1"
            : "0",
          vacacion: mesVacaciones,
          ID_CAMPANIA: CAMPANIA_ACTIVA
        };

        // Agregar sueldos mensuales
        [
          "enero",
          "febrero",
          "marzo",
          "abril",
          "mayo",
          "junio",
          "julio",
          "agosto",
          "septiembre",
          "octubre",
          "noviembre",
          "diciembre",
        ].forEach(function (mes) {
          var switchChecked = $(`#${mes}_switch_sueldo`).is(":checked");
          jsonData[mes] = switchChecked
            ? parseFloat($(`#${mes}_cantidad_sueldo`).val()) || 0
            : 0;
        });

        $.ajax({
          url: isUpdate
            ? `/produccionuva1/produccionuva1_sueldos_cv/${formId}/`
            : "/produccionuva1/produccionuva1_sueldos_cv/",
          type: isUpdate ? "PUT" : "POST",
          contentType: "application/json",
          data: JSON.stringify(jsonData),
          success: function (response) {
            if (response.status === "success") {
              Swal.fire({
                title: isUpdate ? "¡Actualizado!" : "¡Agregado!",
                text: response.message,
                icon: "success",
              }).then(() => {
                tableSueldos.ajax.reload();
                actualizarTotalSueldos();
                $("#ModalSueldoSalario").modal("hide");
                resetearFormularioSueldo();
              });
            }
          },
          error: function (xhr, status, error) {
            Swal.fire({
              title: "Error!",
              text: "Hubo un problema al procesar la solicitud: " + error,
              icon: "error",
            });
          },
          complete: function () {
            // Restaurar el formulario para permitir nuevos envíos
            $form.data("submitting", false);
            $submitButton.prop("disabled", false);
          },
        });
      });

    // Evento para los checkboxes de vacaciones
    $(".vacaciones-checkbox-sueldoSalario").on("change", function () {
      // Desmarcar otros checkboxes de vacaciones
      if (this.checked) {
        $(".vacaciones-checkbox-sueldoSalario")
          .not(this)
          .prop("checked", false);
      }
    });

    // Agregar evento para limpiar el modal cuando se cierra
    $("#ModalSueldoSalario").on("hidden.bs.modal", function () {
      // Limpiar el formulario
      $("#formSueldoSalario")[0].reset();
      $("#formSueldoSalario").removeAttr("data-id");
      $("#check_asignacion_familiar").prop("checked", false);
      $("#asignacion_familiar_total").text("S/. 0.00");
      $("#cantidad_masiva_sueldo").val("");

      // Deshabilitar todos los campos de cantidad y desmarcar switches
      [
        "enero",
        "febrero",
        "marzo",
        "abril",
        "mayo",
        "junio",
        "julio",
        "agosto",
        "septiembre",
        "octubre",
        "noviembre",
        "diciembre",
      ].forEach(function (mes) {
        $(`#${mes}_switch_sueldo`).prop("checked", false);
        $(`#${mes}_cantidad_sueldo`).prop("disabled", true);
        $(`#${mes}_cantidad_sueldo`).val("");
      });

      // Limpiar el total anual
      $("#sueldo_total_anual").text("S/. 0.00");
    });

    // Evento para los switches de meses
    $(".mes-switch").on("change", function () {
      const mes = this.id.replace("_switch_sueldo", "");
      const cantidadInput = $(`#${mes}_cantidad_sueldo`);

      cantidadInput.prop("disabled", !this.checked);
      if (!this.checked) {
        cantidadInput.val("");
      }

      actualizarTotalAnual();
    });
  }

  //-------------------------------------------------------------------------------
  //  INICIALIZACIÓN DE LA TABLA DE SALARIOS
  //-------------------------------------------------------------------------------
  function obtenerTasaCargaSocial_salarios() {
    return $.ajax({
      url: "/configuraciones-sueldos-salarios/",
      type: "GET",
    }).then(function (response) {
      tasaCargaSocialSalario = response.tasa_carga_social_salario;
      montoTransporteSalario = parseFloat(response.monto_transporte);
      montoAlimentacionSalario = parseFloat(response.monto_alimentacion);
    });
  }


  function actualizarFooterSalarios() {

    const year = $('#filtroAnioPresupuesto').val() || 'CAMP' + new Date().getFullYear();

    $.ajax({
      url: "/produccionuva1/produccionuva1_salario_mensual_cv/?year=" + year,
      type: "GET",
      success: function (response) {

        if (!response.data) return;

        const consolidadosPorMes = {};
        let totalAnual = 0;

        response.data.forEach((item) => {

          console.log(item.Mes);
          if (item.Mes !== "Total Anual") {
            consolidadosPorMes[item.Mes.toLowerCase()] = item.Consolidado_Mes;
          } else {
            totalAnual = item.Consolidado_Mes;
          }

        });

        const footer = $(tableSalarios.table().footer());

        Object.keys(consolidadosPorMes).forEach((mes) => {

          footer
            .find(`th[data-mes="${mes}"]`)
            .html(formatearMonto(consolidadosPorMes[mes] || 0));

        });

        footer
          .find('th[data-total="general"]')
          .html(formatearMonto(totalAnual));

      }
    });

  }

  var CAMPANIA_ACTIVA = null;
  function initPresupuestoSalarios() {
    obtenerTasaCargaSocial_salarios().then(function () {
      // var yearVal = $('#filtroAnioPresupuesto').val() || 'CAMP' + new Date().getFullYear();
      CAMPANIA_ACTIVA = $('#filtroAnioPresupuesto').val();

      if (!CAMPANIA_ACTIVA) {
        CAMPANIA_ACTIVA = 'CAMP' + new Date().getFullYear();
      }
      tableSalarios = $("#salariosTable").DataTable({
        //dom: "Bfrtip",
        dom: '<"d-flex justify-content-between align-items-center"Bf>rtip',

        buttons: [
          {
            text: '<i class="fas fa-sync-alt"></i>',
            className: "btn-sm btn-secondary",
            action: function (e, dt, node, config) {
              // Añadir animación de giro
              $(node).find("i").addClass("fa-spin");
              
              // Obtener año actual del filtro
              var currentYear = $('#filtroAnioPresupuesto').val() || 'CAMP' + new Date().getFullYear();

              // Recargar la tabla con el año correcto
              dt.ajax.url("/produccionuva1/produccionuva1_salarios_cv/?year=" + currentYear).load(function () {
                // Callback después de la recarga
                setTimeout(() => {
                  $(node).find("i").removeClass("fa-spin");
                }, 1000);

                // Actualizar totales
                actualizarTotalSalarios();
                actualizarFooterSalarios();
              });
            },
          },
          {
            extend: "excelHtml5",
            title: "REPORTE_PRESUPUESTO",
            text: '<i class="far fa-file-excel"></i> Excel',
            className: "btn-sm btn-success",
            customize: function (xlsx) {
              var sheet = xlsx.xl.worksheets["sheet1.xml"];
              $("row:first c", sheet).attr("s", "2"); // Estilo para encabezados
            },
            excelStyles: {
              template: [
                {
                  id: "2",
                  font: {
                    bold: true,
                    color: "FFFFFF",
                  },
                  fill: {
                    pattern: {
                      bgColor: "2E8B57",
                    },
                  },
                },
              ],
            },
            exportOptions: {
              columns: [
                0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17,
                18, 19,
              ],
              format: {
                body: function (data, row, column) {
                  if (data === null || data === undefined) return "0";

                  // Crear un elemento temporal para remover HTML
                  const temp = document.createElement("div");
                  temp.innerHTML = data;
                  data = temp.textContent || temp.innerText;
                  data = data.trim();

                  // Extraer solo el valor numérico del sueldo (sin la carga social)
                  if (data.includes("S/")) {
                    const valores = data.match(/\d+(\.\d+)?/g);
                    if (valores && valores.length > 0) {
                      return valores[0]; // Retorna solo el primer número encontrado
                    }
                  }

                  if (data.includes("VACACIONES")) {
                    return "0";
                  }

                  return data;
                },
              },
            },
          },
          {
            extend: "pdfHtml5",
            title: "RPT_PRESUPUESTO_SALARIOS",
            text: '<i class="far fa-file-pdf"></i> PDF',
            className: "btn-sm btn-danger",
            orientation: "landscape",
            pageSize: "A4",
            customize: function (doc) {
              // Reducir el tamaño de la fuente
              doc.defaultStyle.fontSize = 6;
              doc.styles.tableHeader.fontSize = 7;
              doc.styles.title.fontSize = 12;

              // Ajustar el ancho de las columnas
              var table = doc.content[1].table.body;
              var colCount = table[0].length;
              var widths = [];
              for (var i = 0; i < colCount; i++) {
                widths.push("*");
              }
              doc.content[1].table.widths = widths;

              // Reducir márgenes
              doc.pageMargins = [10, 10, 10, 10];

              // Ajustar el contenido para que quepa en una página
              doc.content[1].table.keepWithHeaderRows = 1;
              doc.content[1].table.body.forEach(function (row) {
                row.forEach(function (cell) {
                  cell.alignment = "left";
                });
              });
            },
            exportOptions: {
              columns: [
                0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17,
              ], // Excluir la columna de acciones
              format: {
                body: function (data, row, column, node) {
                  // Acortar texto largo si es necesario
                  return data.length > 20 ? data.substr(0, 20) + "..." : data;
                },
              },
            },
          },
          {
            text: '<i class="fas fa-plus mr-1"></i>AGREGAR',
            className: "btn-sm btn-success btn-agregar",
            action: function (e, dt, node, config) {
              $("#ModalSalario").modal("show");
            },
          },
        ],

        scrollX: true,
        scrollY: 250,
        scrollCollapse: true,
        fixedColumns: true,
        serverSide: false,
        pageLength: 7,
        searching: false,
        language: {
          url: dataTableEsUrl,
        },
        ajax: {
          url: "/produccionuva1/produccionuva1_salarios_cv/?year=" + ($('#filtroAnioPresupuesto').val() || 'CAMP' + new Date().getFullYear()),
          dataSrc: "data",
        },
        columns: [
          { data: "id", title: "ID", visible: false },
          {
            data: null,
            title: "N°",
            className: "text-center",
            render: function (data, type, row, meta) {
              // Simplemente usar el índice de la fila + 1
              return meta.row + 1;
            },
          },
          { data: "dni" },
          { data: "nombre" },
          { data: "regimen_laboral" },
          { data: "cargo" },
          { data: "fecha_ingreso" },
          {
            data: "enero",
            render: function (data, type, row) {
              const sueldo = parseFloat(data) || 0;
              let cargaSocial;

              const mesVacaciones = String(row.vacacion).trim();
              const isVacaciones = mesVacaciones === "1";

              // Si no hay sueldo y no hay vacaciones, retornar carga social 0
              if (sueldo === 0 && (mesVacaciones === "0" || !mesVacaciones)) {
                return `S/ 0.00
                          <br>
                          <span class="badge badge-secondary text-dark">
                              S/ 0.00
                          </span>`;
              }

              if (isVacaciones) {
                // Si es mes de vacaciones, buscar sueldo del mes siguiente (febrero)
                // Para enero es especial, solo miramos hacia adelante
                let sueldoReferencia = parseFloat(row.febrero) || 0;

                if (row.asignacion === "1") {
                  cargaSocial =
                    (sueldoReferencia + 0.1 * sueldoMinimo) *
                    tasaCargaSocialSalario;
                } else {
                  cargaSocial = sueldoReferencia * tasaCargaSocialSalario;
                }

                return `<span class="text-info fw-bold" style="font-size: 1.1em; letter-spacing: 0.5px; font-weight: bold;">
                                <i class="fas fa-umbrella-beach me-1"></i> VACACIONES
                            </span>
                            <br>
                            <span class="badge badge-secondary text-dark">
                                S/ ${cargaSocial.toFixed(2)}
                            </span>`;
              } else {
                if (row.asignacion === "1") {
                  cargaSocial =
                    (sueldo + 0.1 * sueldoMinimo) * tasaCargaSocialSalario;
                } else {
                  cargaSocial = sueldo * tasaCargaSocialSalario;
                }

                return `S/ ${sueldo.toFixed(2)}
                            <br>
                            <span class="badge badge-secondary text-dark">
                                S/ ${cargaSocial.toFixed(2)}
                            </span>`;
              }
            },
          },
          {
            data: "febrero",
            render: function (data, type, row) {
              const sueldo = parseFloat(data) || 0;
              let cargaSocial;

              const mesVacaciones = String(row.vacacion).trim();
              const isVacaciones = mesVacaciones === "2";

              // Si no hay sueldo y no hay vacaciones, retornar carga social 0
              if (sueldo === 0 && (mesVacaciones === "0" || !mesVacaciones)) {
                return `S/ 0.00
                          <br>
                          <span class="badge badge-secondary text-dark">
                              S/ 0.00
                          </span>`;
              }

              if (isVacaciones) {
                // Si es mes de vacaciones, buscar sueldo del mes anterior (enero)
                let sueldoReferencia =
                  parseFloat(row.enero) || parseFloat(row.marzo) || 0;

                if (sueldoReferencia === 0) {
                  sueldoReferencia = parseFloat(row.marzo) || 0;
                }
                // EN CASO TENGA ASIGNACION FAMILIAR, SE LE AGREGA EL 10% DEL SUELDO MINIMO
                if (row.asignacion === "1") {
                  cargaSocial =
                    (sueldoReferencia + 0.1 * sueldoMinimo) *
                    tasaCargaSocialSalario;
                } else {
                  cargaSocial = sueldoReferencia * tasaCargaSocialSalario;
                }

                return `<span class="text-info fw-bold" style="font-size: 1.1em; letter-spacing: 0.5px; font-weight: bold;">
                                <i class="fas fa-umbrella-beach me-1"></i> VACACIONES
                            </span>
                            <br>
                            <span class="badge badge-secondary text-dark">
                                S/ ${cargaSocial.toFixed(2)}
                            </span>`;
              } else {
                if (row.asignacion === "1") {
                  cargaSocial =
                    (sueldo + 0.1 * sueldoMinimo) * tasaCargaSocialSalario;
                } else {
                  cargaSocial = sueldo * tasaCargaSocialSalario;
                }

                return `S/ ${sueldo.toFixed(2)}
                            <br>
                            <span class="badge badge-secondary text-dark">
                                S/ ${cargaSocial.toFixed(2)}
                            </span>`;
              }
            },
          },
          {
            data: "marzo",
            render: function (data, type, row) {
              const sueldo = parseFloat(data) || 0;
              let cargaSocial;

              const mesVacaciones = String(row.vacacion).trim();
              const isVacaciones = mesVacaciones === "3";

              // Si no hay sueldo y no hay vacaciones, retornar carga social 0
              if (sueldo === 0 && (mesVacaciones === "0" || !mesVacaciones)) {
                return `S/ 0.00
                          <br>
                          <span class="badge badge-secondary text-dark">
                              S/ 0.00
                          </span>`;
              }

              if (isVacaciones) {
                // Si es mes de vacaciones, buscar sueldo del mes anterior (febrero)
                let sueldoReferencia =
                  parseFloat(row.febrero) || parseFloat(row.abril) || 0;

                if (sueldoReferencia === 0) {
                  sueldoReferencia = parseFloat(row.abril) || 0;
                }

                if (row.asignacion === "1") {
                  cargaSocial =
                    (sueldoReferencia + 0.1 * sueldoMinimo) *
                    tasaCargaSocialSalario;
                } else {
                  cargaSocial = sueldoReferencia * tasaCargaSocialSalario;
                }

                return `<span class="text-info fw-bold" style="font-size: 1.1em; letter-spacing: 0.5px; font-weight: bold;">
                                <i class="fas fa-umbrella-beach me-1"></i> VACACIONES
                            </span>
                            <br>
                            <span class="badge badge-secondary text-dark">
                                S/ ${cargaSocial.toFixed(2)}
                            </span>`;
              } else {
                if (row.asignacion === "1") {
                  cargaSocial =
                    (sueldo + 0.1 * sueldoMinimo) * tasaCargaSocialSalario;
                } else {
                  cargaSocial = sueldo * tasaCargaSocialSalario;
                }

                return `S/ ${sueldo.toFixed(2)}
                            <br>
                            <span class="badge badge-secondary text-dark">
                                S/ ${cargaSocial.toFixed(2)}
                            </span>`;
              }
            },
          },
          {
            data: "abril",
            render: function (data, type, row) {
              const sueldo = parseFloat(data) || 0;
              let cargaSocial = 0;

              // Convertir el valor de vacacion a string para la comparación
              const mesVacaciones = String(row.vacacion).trim();
              const isVacaciones = mesVacaciones === "4";

              // Si no hay sueldo y no hay vacaciones, retornar carga social 0
              if (sueldo === 0 && (mesVacaciones === "0" || !mesVacaciones)) {
                return `S/ 0.00
                          <br>
                          <span class="badge badge-secondary text-dark">
                              S/ 0.00
                          </span>`;
              }

              if (isVacaciones) {
                // Si es mes de vacaciones, buscar sueldo del mes anterior (marzo)
                let sueldoReferencia =
                  parseFloat(row.marzo) || parseFloat(row.mayo) || 0;

                // Si no hay sueldo en marzo, intentar con mayo
                if (sueldoReferencia === 0) {
                  sueldoReferencia = parseFloat(row.mayo) || 0;
                }

                // Calcular carga social usando el sueldo de referencia
                if (row.asignacion === "1") {
                  cargaSocial =
                    (sueldoReferencia + 0.1 * sueldoMinimo) *
                    tasaCargaSocialSalario;
                } else {
                  cargaSocial = sueldoReferencia * tasaCargaSocialSalario;
                }

                // Retornar con estilo especial para vacaciones
                return `<span class="text-info fw-bold" style="font-size: 1.1em; letter-spacing: 0.5px; font-weight: bold;">
                                <i class="fas fa-umbrella-beach me-1"></i> VACACIONES
                            </span>
                            <br>
                            <span class="badge badge-secondary text-dark">
                                S/ ${cargaSocial.toFixed(2)}
                            </span>`;
              } else {
                // Cálculo normal cuando no es mes de vacaciones
                if (row.asignacion === "1") {
                  cargaSocial =
                    (sueldo + 0.1 * sueldoMinimo) * tasaCargaSocialSalario;
                } else {
                  cargaSocial = sueldo * tasaCargaSocialSalario;
                }

                return `S/ ${sueldo.toFixed(2)}
                            <br>
                            <span class="badge badge-secondary text-dark">
                                S/ ${cargaSocial.toFixed(2)}
                            </span>`;
              }
            },
          },
          {
            data: "mayo",
            render: function (data, type, row) {
              const sueldo = parseFloat(data) || 0;
              let cargaSocial;

              // Convertir el valor de vacacion a string para la comparación
              const mesVacaciones = String(row.vacacion).trim();
              const isVacaciones = mesVacaciones === "5";

              // Si no hay sueldo y no hay vacaciones, retornar carga social 0
              if (sueldo === 0 && (mesVacaciones === "0" || !mesVacaciones)) {
                return `S/ 0.00
                          <br>
                          <span class="badge badge-secondary text-dark">
                              S/ 0.00
                          </span>`;
              }

              if (isVacaciones) {
                // Si es mes de vacaciones, buscar sueldo del mes anterior (abril)
                let sueldoReferencia =
                  parseFloat(row.abril) || parseFloat(row.junio) || 0;

                // Si no hay sueldo en abril, intentar con junio
                if (sueldoReferencia === 0) {
                  sueldoReferencia = parseFloat(row.junio) || 0;
                }

                // Calcular carga social usando el sueldo de referencia
                if (row.asignacion === "1") {
                  cargaSocial =
                    (sueldoReferencia + 0.1 * sueldoMinimo) *
                    tasaCargaSocialSalario;
                } else {
                  cargaSocial = sueldoReferencia * tasaCargaSocialSalario;
                }

                // Retornar con estilo especial para vacaciones
                return `<span class="text-info fw-bold" style="font-size: 1.1em; letter-spacing: 0.5px; font-weight: bold;">
                                <i class="fas fa-umbrella-beach me-1"></i> VACACIONES
                            </span>
                            <br>
                            <span class="badge badge-secondary text-dark">
                                S/ ${cargaSocial.toFixed(2)}
                            </span>`;
              } else {
                // Cálculo normal cuando no es mes de vacaciones
                if (row.asignacion === "1") {
                  cargaSocial =
                    (sueldo + 0.1 * sueldoMinimo) * tasaCargaSocialSalario;
                } else {
                  cargaSocial = sueldo * tasaCargaSocialSalario;
                }

                return `S/ ${sueldo.toFixed(2)}
                            <br>
                            <span class="badge badge-secondary text-dark">
                                S/ ${cargaSocial.toFixed(2)}
                            </span>`;
              }
            },
          },
          {
            data: "junio",
            render: function (data, type, row) {
              const sueldo = parseFloat(data) || 0;
              let cargaSocial;

              // Convertir el valor de vacacion a string para la comparación
              const mesVacaciones = String(row.vacacion).trim();
              const isVacaciones = mesVacaciones === "6";

              // Si no hay sueldo y no hay vacaciones, retornar carga social 0
              if (sueldo === 0 && (mesVacaciones === "0" || !mesVacaciones)) {
                return `S/ 0.00
                          <br>
                          <span class="badge badge-secondary text-dark">
                              S/ 0.00
                          </span>`;
              }

              if (isVacaciones) {
                // Si es mes de vacaciones, buscar sueldo del mes anterior (mayo)
                let sueldoReferencia =
                  parseFloat(row.mayo) || parseFloat(row.julio) || 0;

                // Si no hay sueldo en mayo, intentar con julio
                if (sueldoReferencia === 0) {
                  sueldoReferencia = parseFloat(row.julio) || 0;
                }

                // Calcular carga social usando el sueldo de referencia
                if (row.asignacion === "1") {
                  cargaSocial =
                    (sueldoReferencia + 0.1 * sueldoMinimo) *
                    tasaCargaSocialSalario;
                } else {
                  cargaSocial = sueldoReferencia * tasaCargaSocialSalario;
                }

                // Retornar con estilo especial para vacaciones
                return `<span class="text-info fw-bold" style="font-size: 1.1em; letter-spacing: 0.5px; font-weight: bold;">
                                <i class="fas fa-umbrella-beach me-1"></i> VACACIONES
                            </span>
                            <br>
                            <span class="badge badge-secondary text-dark">
                                S/ ${cargaSocial.toFixed(2)}
                            </span>`;
              } else {
                // Cálculo normal cuando no es mes de vacaciones
                if (row.asignacion === "1") {
                  cargaSocial =
                    (sueldo + 0.1 * sueldoMinimo) * tasaCargaSocialSalario;
                } else {
                  cargaSocial = sueldo * tasaCargaSocialSalario;
                }

                return `S/ ${sueldo.toFixed(2)}
                            <br>
                            <span class="badge badge-secondary text-dark">
                                S/ ${cargaSocial.toFixed(2)}
                            </span>`;
              }
            },
          },
          {
            data: "julio",
            render: function (data, type, row) {
              const sueldo = parseFloat(data) || 0;
              let cargaSocial;

              // Convertir el valor de vacacion a string para la comparación
              const mesVacaciones = String(row.vacacion).trim();
              const isVacaciones = mesVacaciones === "7";

              // Si no hay sueldo y no hay vacaciones, retornar carga social 0
              if (sueldo === 0 && (mesVacaciones === "0" || !mesVacaciones)) {
                return `S/ 0.00
                          <br>
                          <span class="badge badge-secondary text-dark">
                              S/ 0.00
                          </span>`;
              }

              if (isVacaciones) {
                // Si es mes de vacaciones, buscar sueldo del mes anterior (junio)
                let sueldoReferencia =
                  parseFloat(row.junio) || parseFloat(row.agosto) || 0;

                // Si no hay sueldo en junio, intentar con agosto
                if (sueldoReferencia === 0) {
                  sueldoReferencia = parseFloat(row.agosto) || 0;
                }

                // Calcular carga social usando el sueldo de referencia
                if (row.asignacion === "1") {
                  cargaSocial =
                    (sueldoReferencia + 0.1 * sueldoMinimo) *
                    tasaCargaSocialSalario;
                } else {
                  cargaSocial = sueldoReferencia * tasaCargaSocialSalario;
                }

                // Retornar con estilo especial para vacaciones
                return `<span class="text-info fw-bold" style="font-size: 1.1em; letter-spacing: 0.5px; font-weight: bold;">
                                <i class="fas fa-umbrella-beach me-1"></i> VACACIONES
                            </span>
                            <br>
                            <span class="badge badge-secondary text-dark">
                                S/ ${cargaSocial.toFixed(2)}
                            </span>`;
              } else {
                // Cálculo normal cuando no es mes de vacaciones
                if (row.asignacion === "1") {
                  cargaSocial =
                    (sueldo + 0.1 * sueldoMinimo) * tasaCargaSocialSalario;
                } else {
                  cargaSocial = sueldo * tasaCargaSocialSalario;
                }

                return `S/ ${sueldo.toFixed(2)}
                            <br>
                            <span class="badge badge-secondary text-dark">
                                S/ ${cargaSocial.toFixed(2)}
                            </span>`;
              }
            },
          },
          {
            data: "agosto",
            render: function (data, type, row) {
              const sueldo = parseFloat(data) || 0;
              let cargaSocial;

              // Convertir el valor de vacacion a string para la comparación
              const mesVacaciones = String(row.vacacion).trim();
              const isVacaciones = mesVacaciones === "8";

              // Si no hay sueldo y no hay vacaciones, retornar carga social 0
              if (sueldo === 0 && (mesVacaciones === "0" || !mesVacaciones)) {
                return `S/ 0.00
                          <br>
                          <span class="badge badge-secondary text-dark">
                              S/ 0.00
                          </span>`;
              }

              if (isVacaciones) {
                // Si es mes de vacaciones, buscar sueldo del mes anterior (julio)
                let sueldoReferencia =
                  parseFloat(row.julio) || parseFloat(row.septiembre) || 0;

                // Si no hay sueldo en julio, intentar con septiembre
                if (sueldoReferencia === 0) {
                  sueldoReferencia = parseFloat(row.septiembre) || 0;
                }

                // Calcular carga social usando el sueldo de referencia
                if (row.asignacion === "1") {
                  cargaSocial =
                    (sueldoReferencia + 0.1 * sueldoMinimo) *
                    tasaCargaSocialSalario;
                } else {
                  cargaSocial = sueldoReferencia * tasaCargaSocialSalario;
                }

                // Retornar con estilo especial para vacaciones
                return `<span class="text-info fw-bold" style="font-size: 1.1em; letter-spacing: 0.5px; font-weight: bold;">
                                <i class="fas fa-umbrella-beach me-1"></i> VACACIONES
                            </span>
                            <br>
                            <span class="badge badge-secondary text-dark">
                                S/ ${cargaSocial.toFixed(2)}
                            </span>`;
              } else {
                // Cálculo normal cuando no es mes de vacaciones
                if (row.asignacion === "1") {
                  cargaSocial =
                    (sueldo + 0.1 * sueldoMinimo) * tasaCargaSocialSalario;
                } else {
                  cargaSocial = sueldo * tasaCargaSocialSalario;
                }

                return `S/ ${sueldo.toFixed(2)}
                            <br>
                            <span class="badge badge-secondary text-dark">
                                S/ ${cargaSocial.toFixed(2)}
                            </span>`;
              }
            },
          },
          {
            data: "septiembre",
            render: function (data, type, row) {
              const sueldo = parseFloat(data) || 0;
              let cargaSocial;

              // Convertir el valor de vacacion a string para la comparación
              const mesVacaciones = String(row.vacacion).trim();
              const isVacaciones = mesVacaciones === "9";

              // Si no hay sueldo y no hay vacaciones, retornar carga social 0
              if (sueldo === 0 && (mesVacaciones === "0" || !mesVacaciones)) {
                return `S/ 0.00
                          <br>
                          <span class="badge badge-secondary text-dark">
                              S/ 0.00
                          </span>`;
              }

              if (isVacaciones) {
                // Si es mes de vacaciones, buscar sueldo del mes anterior (agosto)
                let sueldoReferencia =
                  parseFloat(row.agosto) || parseFloat(row.octubre) || 0;

                // Si no hay sueldo en agosto, intentar con octubre
                if (sueldoReferencia === 0) {
                  sueldoReferencia = parseFloat(row.octubre) || 0;
                }

                // Calcular carga social usando el sueldo de referencia
                if (row.asignacion === "1") {
                  cargaSocial =
                    (sueldoReferencia + 0.1 * sueldoMinimo) *
                    tasaCargaSocialSalario;
                } else {
                  cargaSocial = sueldoReferencia * tasaCargaSocialSalario;
                }

                // Retornar con estilo especial para vacaciones
                return `<span class="text-info fw-bold" style="font-size: 1.1em; letter-spacing: 0.5px; font-weight: bold;">
                                <i class="fas fa-umbrella-beach me-1"></i> VACACIONES
                            </span>
                            <br>
                            <span class="badge badge-secondary text-dark">
                                S/ ${cargaSocial.toFixed(2)}
                            </span>`;
              } else {
                // Cálculo normal cuando no es mes de vacaciones
                if (row.asignacion === "1") {
                  cargaSocial =
                    (sueldo + 0.1 * sueldoMinimo) * tasaCargaSocialSalario;
                } else {
                  cargaSocial = sueldo * tasaCargaSocialSalario;
                }

                return `S/ ${sueldo.toFixed(2)}
                            <br>
                            <span class="badge badge-secondary text-dark">
                                S/ ${cargaSocial.toFixed(2)}
                            </span>`;
              }
            },
          },
          {
            data: "octubre",
            render: function (data, type, row) {
              const sueldo = parseFloat(data) || 0;
              let cargaSocial;

              const mesVacaciones = String(row.vacacion).trim();
              let isVacaciones = row.vacacion === "10"; // Verifica si octubre (mes 10) es el mes de vacaciones

              // Si no hay sueldo y no hay vacaciones, retornar carga social 0
              if (sueldo === 0 && (mesVacaciones === "0" || !mesVacaciones)) {
                return `S/ 0.00
                          <br>
                          <span class="badge badge-secondary text-dark">
                              S/ 0.00
                          </span>`;
              }

              if (isVacaciones) {
                // Si es mes de vacaciones, buscar sueldo del mes anterior (septiembre)
                let sueldoReferencia =
                  parseFloat(row.septiembre) || parseFloat(row.noviembre) || 0;

                // Si no hay sueldo en septiembre, intentar con noviembre
                if (sueldoReferencia === 0) {
                  sueldoReferencia = parseFloat(row.noviembre) || 0;
                }

                // Calcular carga social usando el sueldo de referencia
                if (row.asignacion === "1") {
                  cargaSocial =
                    (sueldoReferencia + 0.1 * sueldoMinimo) *
                    tasaCargaSocialSalario;
                } else {
                  cargaSocial = sueldoReferencia * tasaCargaSocialSalario;
                }

                // Retornar con estilo especial para vacaciones
                return `<span class="text-info fw-bold" style="font-size: 1.1em; letter-spacing: 0.5px; font-weight: bold;">
                                <i class="fas fa-umbrella-beach me-1"></i> VACACIONES
                            </span>
                            <br>
                            <span class="badge badge-secondary text-dark">
                                S/ ${cargaSocial.toFixed(2)}
                            </span>`;
              } else {
                // Cálculo normal cuando no es mes de vacaciones
                if (row.asignacion === "1") {
                  cargaSocial =
                    (sueldo + 0.1 * sueldoMinimo) * tasaCargaSocialSalario;
                } else {
                  cargaSocial = sueldo * tasaCargaSocialSalario;
                }

                return `S/ ${sueldo.toFixed(2)}
                            <br>
                            <span class="badge badge-secondary text-dark">
                                S/ ${cargaSocial.toFixed(2)}
                            </span>`;
              }
            },
          },
          {
            data: "noviembre",
            render: function (data, type, row) {
              const sueldo = parseFloat(data) || 0;
              let cargaSocial;

              const mesVacaciones = String(row.vacacion).trim();
              let isVacaciones = row.vacacion === "11"; // Verifica si noviembre (mes 11) es el mes de vacaciones

              // Si no hay sueldo y no hay vacaciones, retornar carga social 0
              if (sueldo === 0 && (mesVacaciones === "0" || !mesVacaciones)) {
                return `S/ 0.00
                          <br>
                          <span class="badge badge-secondary text-dark">
                              S/ 0.00
                          </span>`;
              }

              if (isVacaciones) {
                // Si es mes de vacaciones, buscar sueldo del mes anterior (octubre)
                let sueldoReferencia =
                  parseFloat(row.octubre) || parseFloat(row.diciembre) || 0;

                // Si no hay sueldo en octubre, intentar con diciembre
                if (sueldoReferencia === 0) {
                  sueldoReferencia = parseFloat(row.diciembre) || 0;
                }

                // Calcular carga social usando el sueldo de referencia
                if (row.asignacion === "1") {
                  cargaSocial =
                    (sueldoReferencia + 0.1 * sueldoMinimo) *
                    tasaCargaSocialSalario;
                } else {
                  cargaSocial = sueldoReferencia * tasaCargaSocialSalario;
                }

                // Retornar con estilo especial para vacaciones
                return `<span class="text-info fw-bold" style="font-size: 1.1em; letter-spacing: 0.5px; font-weight: bold;">
                                <i class="fas fa-umbrella-beach me-1"></i> VACACIONES
                            </span>
                            <br>
                            <span class="badge badge-secondary text-dark">
                                S/ ${cargaSocial.toFixed(2)}
                            </span>`;
              } else {
                // Cálculo normal cuando no es mes de vacaciones
                if (row.asignacion === "1") {
                  cargaSocial =
                    (sueldo + 0.1 * sueldoMinimo) * tasaCargaSocialSalario;
                } else {
                  cargaSocial = sueldo * tasaCargaSocialSalario;
                }

                return `S/ ${sueldo.toFixed(2)}
                            <br>
                            <span class="badge badge-secondary text-dark">
                                S/ ${cargaSocial.toFixed(2)}
                            </span>`;
              }
            },
          },
          {
            data: "diciembre",
            render: function (data, type, row) {
              const sueldo = parseFloat(data) || 0;
              let cargaSocial;

              const mesVacaciones = String(row.vacacion).trim();
              let isVacaciones = row.vacacion === "12"; // Verifica si diciembre (mes 12) es el mes de vacaciones

              // Si no hay sueldo y no hay vacaciones, retornar carga social 0
              if (sueldo === 0 && (mesVacaciones === "0" || !mesVacaciones)) {
                return `S/ 0.00
                          <br>
                          <span class="badge badge-secondary text-dark">
                              S/ 0.00
                          </span>`;
              }

              if (isVacaciones) {
                // Si es mes de vacaciones, buscar sueldo del mes anterior (noviembre)
                let sueldoReferencia =
                  parseFloat(row.noviembre) || parseFloat(row.enero) || 0;

                // Si no hay sueldo en noviembre, intentar con enero del siguiente año
                if (sueldoReferencia === 0) {
                  sueldoReferencia = parseFloat(row.enero) || 0;
                }

                // Calcular carga social usando el sueldo de referencia
                if (row.asignacion === "1") {
                  cargaSocial =
                    (sueldoReferencia + 0.1 * sueldoMinimo) *
                    tasaCargaSocialSalario;
                } else {
                  cargaSocial = sueldoReferencia * tasaCargaSocialSalario;
                }

                // Retornar con estilo especial para vacaciones
                return `<span class="text-info fw-bold" style="font-size: 1.1em; letter-spacing: 0.5px; font-weight: bold;">
                                <i class="fas fa-umbrella-beach me-1"></i> VACACIONES
                            </span>
                            <br>
                            <span class="badge badge-secondary text-dark">
                                S/ ${cargaSocial.toFixed(2)}
                            </span>`;
              } else {
                // Cálculo normal cuando no es mes de vacaciones
                if (row.asignacion === "1") {
                  cargaSocial =
                    (sueldo + 0.1 * sueldoMinimo) * tasaCargaSocialSalario;
                } else {
                  cargaSocial = sueldo * tasaCargaSocialSalario;
                }

                return `S/ ${sueldo.toFixed(2)}
                            <br>
                            <span class="badge badge-secondary text-dark">
                                S/ ${cargaSocial.toFixed(2)}
                            </span>`;
              }
            },
          },

          {
            data: null,
            title: "Total Anual",
            render: function (data, type, row) {
              let totalSueldo = 0;
              let totalCargaSocial = 0;
              let totalTransporte = 0;
              let totalAlimentacion = 0;
              const mesVacaciones = String(row.vacacion).trim();

              // Sumar los valores de todos los meses
              [
                "enero",
                "febrero",
                "marzo",
                "abril",
                "mayo",
                "junio",
                "julio",
                "agosto",
                "septiembre",
                "octubre",
                "noviembre",
                "diciembre",
              ].forEach((mes, index) => {
                const mesActual = String(index + 1);
                const sueldo = parseFloat(row[mes]) || 0;

                if (mesVacaciones === mesActual) {
                  // En mes de vacaciones, calcular carga social con sueldo de referencia
                  let sueldoReferencia;
                  if (index === 0) {
                    // Si es enero, usar febrero como referencia
                    sueldoReferencia = parseFloat(row["febrero"]) || 0;
                  } else {
                    // Usar mes anterior como referencia
                    const mesAnterior = [
                      "enero",
                      "febrero",
                      "marzo",
                      "abril",
                      "mayo",
                      "junio",
                      "julio",
                      "agosto",
                      "septiembre",
                      "octubre",
                      "noviembre",
                      "diciembre",
                    ][index - 1];
                    sueldoReferencia = parseFloat(row[mesAnterior]) || 0;
                  }

                  // Calcular carga social con sueldo de referencia
                  if (row.asignacion === "1") {
                    totalCargaSocial +=
                      (sueldoReferencia + 0.1 * sueldoMinimo) *
                      tasaCargaSocialSalario;
                  } else {
                    totalCargaSocial +=
                      sueldoReferencia * tasaCargaSocialSalario;
                  }
                } else {
                  // Mes normal
                  if (sueldo > 0) {
                    totalSueldo += sueldo;
                    // Calcular carga social normal
                    if (row.asignacion === "1") {
                      totalCargaSocial +=
                        (sueldo + 0.1 * sueldoMinimo) * tasaCargaSocialSalario;
                    } else {
                      totalCargaSocial += sueldo * tasaCargaSocialSalario;
                    }
                    // Calcular transporte y alimentación
                    totalTransporte += montoTransporte * 26;
                    totalAlimentacion += montoAlimentacion * 26;
                  }
                }
              });

              return `
                    <div class="d-flex flex-column" style="gap: 3px;">
                        <!-- Sueldo Base -->
                        <div class="text-right" style="font-weight: bold;">
                            S/ ${totalSueldo.toFixed(2)}
                        </div>
                        
                        <!-- Primera fila: Carga Social y Transporte -->
                        <div class="d-flex justify-content-end" style="gap: 5px;">
                            <span class="badge badge-secondary text-dark" 
                                  style="min-width: 85px; font-size: 11px;" 
                                  title="Carga Social">
                                <i class="fas fa-money"></i>
                                S/ ${totalCargaSocial.toFixed(2)}
                            </span>
                            
                            <span class="badge badge-info text-dark" 
                                  style="min-width: 85px; font-size: 11px;" 
                                  title="Transporte">
                                <i class="fas fa-bus"></i>
                                S/ ${totalTransporte.toFixed(2)}
                            </span>
                        </div>
                        
                        <!-- Segunda fila: Alimentación y Asignación Familiar -->
                        <div class="d-flex justify-content-end" style="gap: 5px;">
                            <span class="badge badge-warning text-dark" 
                                  style="min-width: 85px; font-size: 11px;" 
                                  title="Alimentación">
                                <i class="fas fa-utensils"></i>
                                S/ ${totalAlimentacion.toFixed(2)}
                            </span>
                            
                            ${
                              row.asignacion === "1"
                                ? `<span class="badge badge-success text-dark" 
                                        style="min-width: 85px; font-size: 11px; background-color: #bfff00;" 
                                        title="Asignación Familiar">
                                        <i class="fas fa-users"></i>
                                        S/ ${(0.1 * sueldoMinimo * 12).toFixed(
                                          2
                                        )}
                                    </span>`
                                : `<span style="min-width: 85px;"></span>`
                            }
                        </div>
                    </div>
                `;
            },
          },

          {
            data: null,
            title: "Acciones",
            className: "sticky-col",
            render: function (data, type, row) {
              return (
                '<div class="d-flex justify-content-around">' +
                '<button class="btn  btn-danger delete-btn " data-id="' +
                row.id +
                '" title="Eliminar">' +
                '<i class="fas fa-trash fa-sm"></i>' +
                "</button>" +
                '<button class="btn  btn-primary edit-btn " data-id="' +
                row.id +
                '" title="Editar">' +
                '<i class="fas fa-edit fa-sm"></i>' +
                "</button>" +
                "</div>"
              );
            },
            orderable: false,
          },
        ],

        columnDefs: [
          {
            targets: [0, 1, 2, 3, 4, 5],
            className: "dt-body-left",
          },
          {
            targets: "_all",
            className: "dt-body-right",
          },
        ],
        responsive: true,
        ordering: true,
        order: [[0, "desc"]],
        language: {
          url: dataTableEsUrl,
        },

        
      });

      tableSalarios.on('xhr', function () {
        actualizarFooterSalarios();
      });

    });

    actualizarTotalSalarios();

    // Evento para eliminar
    $("#salariosTable tbody").on("click", ".delete-btn", function () {
      var id = $(this).data("id");
      eliminarSalario(id);
    });

    // Evento para editar
    $("#salariosTable tbody").on("click", ".edit-btn", function () {
      var id = $(this).data("id");
      editarSalario(id);
    });

    // Manejo del formulario
    $("#formSalario")
      .off("submit")
      .on("submit", function (e) {
        e.preventDefault();

        // Prevenir múltiples envíos
        const $form = $(this);
        const $submitButton = $form.find('button[type="submit"]');

        // Si el formulario ya está siendo enviado, detener
        if ($form.data("submitting")) {
          return false;
        }

        // Marcar el formulario como en proceso de envío
        $form.data("submitting", true);
        $submitButton.prop("disabled", true);

        let tieneMesesAsignados = false;
        let mesVacaciones = "0"; // Valor por defecto para vacaciones

        // Obtener el mes de vacaciones seleccionado
        $(".vacaciones-checkbox-sueldo").each(function () {
          if ($(this).is(":checked")) {
            const mes = this.id.replace("_vacaciones_sueldo", "");
            mesVacaciones = obtenerNumeroMes(mes);
          }
        });

        // Verificar meses con salario asignado y vacaciones
        [
          "enero",
          "febrero",
          "marzo",
          "abril",
          "mayo",
          "junio",
          "julio",
          "agosto",
          "septiembre",
          "octubre",
          "noviembre",
          "diciembre",
        ].forEach(function (mes) {
          if (
            $(`#${mes}_switch_salario`).is(":checked") &&
            parseFloat($(`#${mes}_cantidad_salario`).val()) > 0
          ) {
            tieneMesesAsignados = true;
          }
          if ($(`#${mes}_vacaciones_sueldo`).is(":checked")) {
            mesVacaciones = obtenerNumeroMes(mes);
          }
        });

        if (!tieneMesesAsignados) {
          Swal.fire({
            title: "Error!",
            text: "Debe asignar salario a al menos un mes",
            icon: "error",
          });
          // Restaurar el formulario para permitir nuevo intento
          $form.data("submitting", false);
          $submitButton.prop("disabled", false);
          return false;
        }

        var formId = $(this).attr("data-id");
        var isUpdate = formId !== undefined;

        CAMPANIA_ACTIVA = $('#filtroAnioPresupuesto').val() || 'CAMP' + new Date().getFullYear();

        var jsonData = {
          dni: $("#dni_salario").val(),
          nombre: $("#nombre_salario").val(),
          regimen_laboral: $("#regimen_laboral_salario").val(),
          cargo: $("#cargo_salario").val(),
          fecha_ingreso: $("#fecha_ingreso_salario").val(),
          asignacion: $("#check_asignacion_familiar_salario").is(":checked")
            ? "1"
            : "0",
          vacacion: mesVacaciones,
          ID_CAMPANIA: CAMPANIA_ACTIVA
        };

        // Agregar salarios mensuales
        [
          "enero",
          "febrero",
          "marzo",
          "abril",
          "mayo",
          "junio",
          "julio",
          "agosto",
          "septiembre",
          "octubre",
          "noviembre",
          "diciembre",
        ].forEach(function (mes) {
          var switchChecked = $(`#${mes}_switch_salario`).is(":checked");
          jsonData[mes] = switchChecked
            ? parseFloat($(`#${mes}_cantidad_salario`).val()) || 0
            : 0;
        });

        $.ajax({
          url: isUpdate
            ? `/produccionuva1/produccionuva1_salarios_cv/${formId}/`
            : "/produccionuva1/produccionuva1_salarios_cv/",
          type: isUpdate ? "PUT" : "POST",
          contentType: "application/json",
          data: JSON.stringify(jsonData),
          success: function (response) {
            if (response.status === "success") {
              Swal.fire({
                title: isUpdate ? "¡Actualizado!" : "¡Agregado!",
                text: response.message,
                icon: "success",
              }).then(() => {
                tableSalarios.ajax.reload();
                actualizarTotalSalarios();
                $("#ModalSalario").modal("hide");
                resetearFormularioSalario();
              });
            }
          },
          error: function (xhr, status, error) {
            Swal.fire({
              title: "Error!",
              text: "Hubo un problema al procesar la solicitud: " + error,
              icon: "error",
            });
          },
          complete: function () {
            // Restaurar el formulario para permitir nuevos envíos
            $form.data("submitting", false);
            $submitButton.prop("disabled", false);
          },
        });
      });

    // Agregar evento para limpiar el modal cuando se cierra
    $("#ModalSalario").on("hidden.bs.modal", function () {
      resetearFormularioSalario();
      // Limpiar el formulario
      $("#formSalario")[0].reset();
      $("#formSalario").removeAttr("data-id");
      $("#check_asignacion_familiar_salario").prop("checked", false);
      $("#asignacion_familiar_total_salario").text("S/. 0.00");
      $("#cantidad_masiva_salario").val("");

      // Deshabilitar todos los campos de cantidad y desmarcar switches
      [
        "enero",
        "febrero",
        "marzo",
        "abril",
        "mayo",
        "junio",
        "julio",
        "agosto",
        "septiembre",
        "octubre",
        "noviembre",
        "diciembre",
      ].forEach(function (mes) {
        $(`#${mes}_switch_salario`).prop("checked", false);
        $(`#${mes}_cantidad_salario`).prop("disabled", true);
        $(`#${mes}_cantidad_salario`).val("");
      });

      // Limpiar el total anual
      $("#salario_total_anual").text("S/. 0.00");
    });

    // Evento para los switches de meses
    $('input[type="checkbox"][id$="_switch_salario"]').on(
      "change",
      function () {
        const mes = this.id.replace("_switch_salario", "");
        const cantidadInput = $(`#${mes}_cantidad_salario`);

        cantidadInput.prop("disabled", !this.checked);
        if (!this.checked) {
          cantidadInput.val("");
        }

        actualizarTotalAnual_Salarios();
      }
    );
  }

  //-------------------------------------------------------------------------------
  //  FUNCIONES DE EDICIÓN / ELIMINACIÓN (SUELDOS / SALARIOS)
  //-------------------------------------------------------------------------------
  function eliminarSueldo(id) {
    Swal.fire({
      title: "¿Está seguro?",
      text: "Esta acción no se puede deshacer",
      icon: "warning",
      showCancelButton: true,
      confirmButtonColor: "#3085d6",
      cancelButtonColor: "#d33",
      confirmButtonText: "Sí, eliminar",
      cancelButtonText: "Cancelar",
    }).then((result) => {
      if (result.isConfirmed) {
        $.ajax({
          url: `/produccionuva1/produccionuva1_sueldos_cv/${id}/`,
          type: "DELETE",
          success: function (response) {
            if (response.status === "success") {
              Swal.fire("¡Eliminado!", response.message, "success");
              table.ajax.reload();
              actualizarTotalSueldos();
            }
          },
          error: function () {
            Swal.fire("Error", "No se pudo eliminar el registro", "error");
          },
        });
      }
    });
  }

  function eliminarSalario(id) {
    Swal.fire({
      title: "¿Está seguro?",
      text: "Esta acción no se puede deshacer",
      icon: "warning",
      showCancelButton: true,
      confirmButtonColor: "#3085d6",
      cancelButtonColor: "#d33",
      confirmButtonText: "Sí, eliminar",
      cancelButtonText: "Cancelar",
    }).then((result) => {
      if (result.isConfirmed) {
        $.ajax({
          url: `/produccionuva1/produccionuva1_salarios_cv/${id}/`,
          type: "DELETE",
          success: function (response) {
            if (response.status === "success") {
              Swal.fire("¡Eliminado!", response.message, "success");
              tableSalarios.ajax.reload();
              actualizarTotalSalarios();
            }
          },
          error: function () {
            Swal.fire("Error", "No se pudo eliminar el registro", "error");
          },
        });
      }
    });
  }

  // Editar Sueldo
  function editarSueldo(id) {
    let intentos = 0;
    const maxIntentos = 3;

    Swal.fire({
      title: "Cargando datos...",
      text: "Por favor espere",
      allowOutsideClick: false,
      didOpen: () => {
        Swal.showLoading();
      },
    });

    function llenarFormularioSueldo(data) {
      return new Promise((resolve, reject) => {
        try {
          resetearFormularioSueldo();
          $("#ModalSueldoSalario").one("shown.bs.modal", function () {
            $("#dni_sueldo_salario").val(data.dni || "");
            $("#nombre_sueldo_salario").val(data.nombre || "");
            $("#regimen_laboral_sueldo_salario").val(
              data.regimen_laboral || ""
            );
            $("#cargo_sueldo_salario").val(data.cargo || "");
            $("#fecha_ingreso_sueldo_salario").val(data.fecha_ingreso || "");
            $("#check_asignacion_familiar").prop(
              "checked",
              data.asignacion === "1"
            );

            $(".vacaciones-checkbox-sueldoSalario").prop("checked", false);
            $(".custom-switch-container").removeClass("vacaciones");
            $(".vacaciones-checkbox-sueldoSalario").prop("disabled", false);

            if (data.vacacion && data.vacacion !== "0") {
              const meses = {
                1: "enero",
                2: "febrero",
                3: "marzo",
                4: "abril",
                5: "mayo",
                6: "junio",
                7: "julio",
                8: "agosto",
                9: "septiembre",
                10: "octubre",
                11: "noviembre",
                12: "diciembre",
              };
              const mesVacacionNum = parseInt(data.vacacion);
              const mesVacaciones = meses[mesVacacionNum];

              if (mesVacaciones) {
                const checkboxVacaciones = $(
                  `#${mesVacaciones}_vacaciones_sueldoSalario`
                );
                const switchElement = $(`#${mesVacaciones}_switch_sueldo`);
                const inputElement = $(`#${mesVacaciones}_cantidad_sueldo`);

                checkboxVacaciones.prop("checked", true).trigger("change");
                checkboxVacaciones
                  .closest(".custom-switch-container")
                  .addClass("vacaciones");
                switchElement.prop("checked", false).prop("disabled", true);
                inputElement.val("").prop("disabled", true);
                $(".vacaciones-checkbox-sueldoSalario")
                  .not(checkboxVacaciones)
                  .prop("disabled", true);
              }
            }

            [
              "enero",
              "febrero",
              "marzo",
              "abril",
              "mayo",
              "junio",
              "julio",
              "agosto",
              "septiembre",
              "octubre",
              "noviembre",
              "diciembre",
            ].forEach(function (mes) {
              const valor = parseFloat(data[mes]) || 0;
              const switchElement = $(`#${mes}_switch_sueldo`);
              const inputElement = $(`#${mes}_cantidad_sueldo`);

              if (valor > 0) {
                switchElement.prop("checked", true);
                inputElement.prop("disabled", false).val(valor.toFixed(2));
              } else {
                switchElement.prop("checked", false);
                inputElement.prop("disabled", true).val("");
              }
            });

            $("#formSueldoSalario").attr("data-id", id);

            setTimeout(() => {
              actualizarTotalAnual();
              calcularAsignacionFamiliar();
              calcularTransporteAlimentacion();
              resolve();
            }, 100);
          });
          $("#ModalSueldoSalario").modal("show");
        } catch (error) {
          reject(error);
        }
      });
    }

    function intentarCargarDatos() {
      $.ajax({
        url: `/produccionuva1/produccionuva1_sueldos_cv/${id}/`,
        type: "GET",
        success: function (data) {
          if (!data || !data.dni) {
            intentos++;
            if (intentos < maxIntentos) {
              setTimeout(intentarCargarDatos, 1000);
              return;
            } else {
              Swal.fire({
                icon: "error",
                title: "Error de carga",
                text: "No se pudieron recuperar los datos después de varios intentos",
              });
              return;
            }
          }
          llenarFormularioSueldo(data)
            .then(() => {
              Swal.close();
            })
            .catch(() => {
              Swal.fire({
                icon: "error",
                title: "Error",
                text: "Error al llenar el formulario",
              });
            });
        },
        error: function () {
          intentos++;
          if (intentos < maxIntentos) {
            setTimeout(intentarCargarDatos, 1000);
          } else {
            Swal.fire({
              icon: "error",
              title: "Error de conexión",
              text: "No se pudo establecer conexión con el servidor",
            });
          }
        },
      });
    }

    intentarCargarDatos();
  }

  // Editar Salario
  function editarSalario(id) {
    let intentos = 0;
    const maxIntentos = 3;

    Swal.fire({
      title: "Cargando datos...",
      text: "Por favor espere",
      allowOutsideClick: false,
      didOpen: () => {
        Swal.showLoading();
      },
    });

    function llenarFormularioSalario(data) {
      return new Promise((resolve, reject) => {
        try {
          resetearFormularioSalario();
          $("#ModalSalario").one("shown.bs.modal", function () {
            $("#dni_salario").val(data.dni || "");
            $("#nombre_salario").val(data.nombre || "");
            $("#regimen_laboral_salario").val(data.regimen_laboral || "");
            $("#cargo_salario").val(data.cargo || "");
            $("#fecha_ingreso_salario").val(data.fecha_ingreso || "");
            $("#check_asignacion_familiar_salario").prop(
              "checked",
              data.asignacion === "1"
            );

            $(".vacaciones-checkbox-sueldo").prop("checked", false);
            $(".custom-switch-container").removeClass("vacaciones");
            $(".vacaciones-checkbox-sueldo").prop("disabled", false);

            if (data.vacacion && data.vacacion !== "0") {
              const meses = {
                1: "enero",
                2: "febrero",
                3: "marzo",
                4: "abril",
                5: "mayo",
                6: "junio",
                7: "julio",
                8: "agosto",
                9: "septiembre",
                10: "octubre",
                11: "noviembre",
                12: "diciembre",
              };
              const mesVacacionNum = parseInt(data.vacacion);
              const mesVacaciones = meses[mesVacacionNum];

              if (mesVacaciones) {
                const checkboxVacaciones = $(
                  `#${mesVacaciones}_vacaciones_sueldo`
                );
                const switchElement = $(`#${mesVacaciones}_switch_salario`);
                const inputElement = $(`#${mesVacaciones}_cantidad_salario`);

                checkboxVacaciones.prop("checked", true).trigger("change");
                checkboxVacaciones
                  .closest(".custom-switch-container")
                  .addClass("vacaciones");
                switchElement.prop("checked", false).prop("disabled", true);
                inputElement.val("").prop("disabled", true);
                $(".vacaciones-checkbox-sueldo")
                  .not(checkboxVacaciones)
                  .prop("disabled", true);
              }
            }

            [
              "enero",
              "febrero",
              "marzo",
              "abril",
              "mayo",
              "junio",
              "julio",
              "agosto",
              "septiembre",
              "octubre",
              "noviembre",
              "diciembre",
            ].forEach(function (mes) {
              const valor = parseFloat(data[mes]) || 0;
              const switchElement = $(`#${mes}_switch_salario`);
              const inputElement = $(`#${mes}_cantidad_salario`);

              if (valor > 0) {
                switchElement.prop("checked", true);
                inputElement.prop("disabled", false).val(valor.toFixed(2));
              } else {
                switchElement.prop("checked", false);
                inputElement.prop("disabled", true).val("");
              }
            });

            $("#formSalario").attr("data-id", id);

            setTimeout(() => {
              actualizarTotalAnual_Salarios();
              calcularAsignacionFamiliar_Salarios();
              calcularTransporteAlimentacion_Salarios();
              resolve();
            }, 100);
          });
          $("#ModalSalario").modal("show");
        } catch (error) {
          reject(error);
        }
      });
    }

    function intentarCargarDatos() {
      $.ajax({
        url: `/produccionuva1/produccionuva1_salarios_cv/${id}/`,
        type: "GET",
        success: function (data) {
          if (!data || !data.dni) {
            intentos++;
            if (intentos < maxIntentos) {
              setTimeout(intentarCargarDatos, 1000);
              return;
            } else {
              Swal.fire({
                icon: "error",
                title: "Error de carga",
                text: "No se pudieron recuperar los datos después de varios intentos",
              });
              return;
            }
          }
          llenarFormularioSalario(data)
            .then(() => {
              Swal.close();
            })
            .catch(() => {
              Swal.fire({
                icon: "error",
                title: "Error",
                text: "Error al llenar el formulario de salario",
              });
            });
        },
        error: function () {
          intentos++;
          if (intentos < maxIntentos) {
            setTimeout(intentarCargarDatos, 1000);
          } else {
            Swal.fire({
              icon: "error",
              title: "Error de conexión",
              text: "No se pudo establecer conexión con el servidor",
            });
          }
        },
      });
    }

    intentarCargarDatos();
  }

  //-------------------------------------------------------------------------------
  //  CÁLCULOS DE ASIGNACIÓN, TRANSPORTE Y ALIMENTACIÓN (SUELDOS / SALARIOS)
  //-------------------------------------------------------------------------------
  function calcularAsignacionFamiliar() {
    if (!$("#check_asignacion_familiar").is(":checked")) {
      $("#asignacion_familiar_total").text("S/. 0.00");
      return;
    }
    let mesesConSueldo = 0;
    const asignacionPorMes = sueldoMinimo * 0.1;
    [
      "enero",
      "febrero",
      "marzo",
      "abril",
      "mayo",
      "junio",
      "julio",
      "agosto",
      "septiembre",
      "octubre",
      "noviembre",
      "diciembre",
    ].forEach(function (mes) {
      if ($(`#${mes}_switch_sueldo`).is(":checked")) {
        mesesConSueldo++;
      }
    });
    const totalAsignacion = asignacionPorMes * mesesConSueldo;
    $("#asignacion_familiar_total").text(`S/. ${totalAsignacion.toFixed(2)}`);
  }

  function calcularAsignacionFamiliar_Salarios() {
    if (!$("#check_asignacion_familiar_salario").is(":checked")) {
      $("#asignacion_familiar_total_salario").text("S/. 0.00");
      return;
    }
    let mesesConSalario = 0;
    const asignacionPorMes = sueldoMinimo * 0.1;
    [
      "enero",
      "febrero",
      "marzo",
      "abril",
      "mayo",
      "junio",
      "julio",
      "agosto",
      "septiembre",
      "octubre",
      "noviembre",
      "diciembre",
    ].forEach(function (mes) {
      if ($(`#${mes}_switch_salario`).is(":checked")) {
        mesesConSalario++;
      }
    });
    const totalAsignacion = asignacionPorMes * mesesConSalario;
    $("#asignacion_familiar_total_salario").text(
      `S/. ${totalAsignacion.toFixed(2)}`
    );
  }

  function calcularTransporteAlimentacion() {
    let mesesConSueldo = 0;
    [
      "enero",
      "febrero",
      "marzo",
      "abril",
      "mayo",
      "junio",
      "julio",
      "agosto",
      "septiembre",
      "octubre",
      "noviembre",
      "diciembre",
    ].forEach(function (mes) {
      if ($(`#${mes}_switch_sueldo`).is(":checked")) {
        mesesConSueldo++;
      }
    });
    const totalTransporte = montoTransporte * 26 * mesesConSueldo;
    const totalAlimentacion = montoAlimentacion * 26 * mesesConSueldo;
    $("#transporte_total").text(`S/. ${totalTransporte.toFixed(2)}`);
    $("#alimentacion_total").text(`S/. ${totalAlimentacion.toFixed(2)}`);
  }

  function calcularTransporteAlimentacion_Salarios() {
    let mesesConSalario = 0;
    [
      "enero",
      "febrero",
      "marzo",
      "abril",
      "mayo",
      "junio",
      "julio",
      "agosto",
      "septiembre",
      "octubre",
      "noviembre",
      "diciembre",
    ].forEach(function (mes) {
      if ($(`#${mes}_switch_salario`).is(":checked")) {
        mesesConSalario++;
      }
    });
    const totalTransporte = montoTransporteSalario * 26 * mesesConSalario;
    const totalAlimentacion = montoAlimentacionSalario * 26 * mesesConSalario;
    $("#transporte_total_salario").text(`S/. ${totalTransporte.toFixed(2)}`);
    $("#alimentacion_total_salario").text(
      `S/. ${totalAlimentacion.toFixed(2)}`
    );
  }

  //-------------------------------------------------------------------------------
  //  CÁLCULO DE TOTALES ANUALES
  //-------------------------------------------------------------------------------
  function actualizarTotalAnual() {
    let total = 0;
    let totalAsignacionFamiliar = 0;
    [
      "enero",
      "febrero",
      "marzo",
      "abril",
      "mayo",
      "junio",
      "julio",
      "agosto",
      "septiembre",
      "octubre",
      "noviembre",
      "diciembre",
    ].forEach(function (mes) {
      if ($(`#${mes}_switch_sueldo`).is(":checked")) {
        total += parseFloat($(`#${mes}_cantidad_sueldo`).val()) || 0;
      }
    });
    if ($("#check_asignacion_familiar").is(":checked")) {
      totalAsignacionFamiliar = sueldoMinimo * 0.1 * 12;
    }

    $("#sueldo_total_anual").text(`S/. ${total.toFixed(2)}`);

    // EN CASO TENGA ASIGNACION FAMILIAR, SE LE AGREGA EL 10% DEL SUELDO MINIMO
    if ($("#check_asignacion_familiar").is(":checked")) {
      let sueldoMes = total / 12;
      let asignacionMes = totalAsignacionFamiliar / 12;
      let totalCargasocialAsignacion =
        (sueldoMes + asignacionMes) * tasaCargaSocialSueldo * 12;
      $("#Cargas_Sociales").text(
        `S/. ${totalCargasocialAsignacion.toFixed(2)}`
      );
    } else {
      $("#Cargas_Sociales").text(
        `S/. ${(total * tasaCargaSocialSueldo).toFixed(2)}`
      );
    }

    $("#asignacion_familiar_total").text(
      `S/. ${totalAsignacionFamiliar.toFixed(2)}`
    );
    calcularAsignacionFamiliar();
    calcularTransporteAlimentacion();
  }

  function actualizarTotalAnual_Salarios() {
    let total = 0;
    let totalAsignacionFamiliar = 0;
    [
      "enero",
      "febrero",
      "marzo",
      "abril",
      "mayo",
      "junio",
      "julio",
      "agosto",
      "septiembre",
      "octubre",
      "noviembre",
      "diciembre",
    ].forEach(function (mes) {
      if ($(`#${mes}_switch_salario`).is(":checked")) {
        total += parseFloat($(`#${mes}_cantidad_salario`).val()) || 0;
      }
    });
    if ($("#check_asignacion_familiar_salario").is(":checked")) {
      totalAsignacionFamiliar = sueldoMinimo * 0.1 * 12;
    }
    $("#salario_total_anual").text(`S/. ${total.toFixed(2)}`);

    //####################################################
    // EN CASO TENGA ASIGNACION FAMILIAR, SE LE AGREGA EL 10% DEL SUELDO MINIMO
    //####################################################

    if ($("#check_asignacion_familiar").is(":checked")) {
      let sueldoMesSalario = total / 12;
      let asignacionMesSalario = totalAsignacionFamiliar / 12;
      let totalCargasocialAsignacionSalario =
        (sueldoMesSalario + asignacionMesSalario) * tasaCargaSocialSalario * 12;

      $("#Cargas_Sociales_salario").text(
        `S/. ${totalCargasocialAsignacionSalario.toFixed(2)}`
      );
    } else {
      $("#Cargas_Sociales_salario").text(
        `S/. ${(total * tasaCargaSocialSalario).toFixed(2)}`
      );
    }

    $("#asignacion_familiar_total_salario").text(
      `S/. ${totalAsignacionFamiliar.toFixed(2)}`
    );
    calcularAsignacionFamiliar_Salarios();
    calcularTransporteAlimentacion_Salarios();
  }

  //-------------------------------------------------------------------------------
  //  RESETEAR FORMULARIOS
  //-------------------------------------------------------------------------------

  function resetearFormularioSueldo() {
    $("#formSueldoSalario")[0].reset();
    $("#formSueldoSalario").removeAttr("data-id");
    $("#check_asignacion_familiar").prop("checked", false);
    $("#sueldo_total_anual").text("S/. 0.00");
    $("#Cargas_Sociales").text("S/. 0.00");
    $("#asignacion_familiar_total").text("S/. 0.00");
    $("#transporte_total").text("S/. 0.00");
    $("#alimentacion_total").text("S/. 0.00");
    $("#cantidad_masiva_sueldo").val("");
    [
      "enero",
      "febrero",
      "marzo",
      "abril",
      "mayo",
      "junio",
      "julio",
      "agosto",
      "septiembre",
      "octubre",
      "noviembre",
      "diciembre",
    ].forEach(function (mes) {
      $(`#${mes}_switch_sueldo`).prop("checked", false);
      $(`#${mes}_cantidad_sueldo`).prop("disabled", true).val("");
    });
    $("#dni_sueldo_salario").val("");
    $("#nombre_sueldo_salario").val("");
    $("#regimen_laboral_sueldo_salario").val("");
    $("#cargo_sueldo_salario").val("");
    $("#fecha_ingreso_sueldo_salario").val("");
  }

  function resetearFormularioSalario() {
    $("#formSalario")[0].reset();
    $("#formSalario").removeAttr("data-id");
    $("#check_asignacion_familiar_salario").prop("checked", false);
    $("#salario_total_anual").text("S/. 0.00");
    $("#Cargas_Sociales_salario").text("S/. 0.00");
    $("#asignacion_familiar_total_salario").text("S/. 0.00");
    $("#transporte_total_salario").text("S/. 0.00");
    $("#alimentacion_total_salario").text("S/. 0.00");
    $("#cantidad_masiva_salario").val("");
    [
      "enero",
      "febrero",
      "marzo",
      "abril",
      "mayo",
      "junio",
      "julio",
      "agosto",
      "septiembre",
      "octubre",
      "noviembre",
      "diciembre",
    ].forEach(function (mes) {
      $(`#${mes}_switch_salario`).prop("checked", false);
      $(`#${mes}_cantidad_salario`).prop("disabled", true).val("");
    });
    $("#dni_salario").val("");
    $("#nombre_salario").val("");
    $("#regimen_laboral_salario").val("");
    $("#cargo_salario").val("");
    $("#fecha_ingreso_salario").val("");
  }
}
