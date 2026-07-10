$(document).ready(function () {
  // Ocultar el formulario al inicio
  $("#userInfoForm").hide();

  // 🔥 FILTRAR SOLO BBVA Y BCP
  const bancosPermitidos = ["BANCO CONTINENTAL BBVA", "BANCO DE CREDITO DEL PERU"];

  $('select[name="banco"] option').each(function () {
    const texto = $(this).text().trim().toUpperCase();

    if ($(this).val() !== "" && !bancosPermitidos.includes(texto)) {
    $(this).remove();
  }
  });
  
  // Variable global para almacenar los datos de utilidades
  let datosUtilidades = null;

  // Variable para contar intentos de validación de fecha de nacimiento
  let intentosValidacion = 0;
  const MAX_INTENTOS = 3;

  // Función para verificar si un DNI tiene utilidades
  /* function verificarUtilidades(dni) {
    // Mostrar cargando
    Swal.fire({
      title: "Verificando datos",
      text: "Espere un momento...",
      allowOutsideClick: false,
      didOpen: () => {
        Swal.showLoading();
      },
    });

    // Primero obtener los datos personales del usuario
    $.ajax({
      url: `/rrhh/datos_personal_por_dni/?dni=${dni}`,
      type: "GET",
      dataType: "json",
      success: function (personalResponse) {
        if (personalResponse.status === "success" && personalResponse.data) {
          // Si encontramos datos personales, verificar utilidades
          $.ajax({
            url: `/rrhh/certificado_utilidades/?periodo=202504&factor=1`,
            type: "GET",
            dataType: "json",
            success: function (utilidadesResponse) {
              Swal.close();

              if (
                utilidadesResponse.status === "success" &&
                utilidadesResponse.data &&
                utilidadesResponse.data.length > 0
              ) {
                // Buscar si el DNI está en los datos de utilidades
                const usuarioConUtilidades = utilidadesResponse.data.find(
                  (item) => item.DNI === dni || item.DOCUMENTO === dni
                );

                if (usuarioConUtilidades) {
                  // Guardar los datos de utilidades para generar el PDF después
                  datosUtilidades = usuarioConUtilidades;
                  console.log("Datos para el PDF:", datosUtilidades);

                  // Antes de obtener los datos adicionales, solicitar la fecha de nacimiento
                  solicitarFechaNacimiento(dni);
                } else {
                  Swal.fire({
                    icon: "warning",
                    title: "No cuenta con utilidades",
                    text: "El usuario no tiene utilidades asignadas en el periodo actual. Por favor comuníquese con el área de Recursos Humanos para más información. Nota: Este proceso no aplica para trabajadores activos.",
                  });
                }
              } else {
                Swal.fire({
                  icon: "error",
                  title: "Error",
                  text: "No se pudieron obtener los datos de utilidades.",
                  confirmButtonText: "Entendido",
                });
              }
            },
            error: function (xhr, status, error) {
              Swal.close();
              console.error("Error al verificar utilidades:", error);
              Swal.fire({
                icon: "error",
                title: "Error",
                text: "Ocurrió un error al verificar las utilidades del usuario.",
                confirmButtonText: "Entendido",
              });
            },
          });
        } else {
          Swal.close();

          Swal.fire({
            icon: "warning",
            title: "Usuario no encontrado",
            text: "No se encontró información para el DNI proporcionado.",
            confirmButtonText: "Entendido",
          });
        }
      },
      error: function (xhr, status, error) {
        Swal.close();
        console.error("Error al buscar datos personales:", error);
        Swal.fire({
          icon: "error",
          title: "Error",
          text: "Ocurrió un error al buscar datos del usuario.",
          confirmButtonText: "Entendido",
        });
      },
    });
  } */

  function verificarUtilidades(dni) {
    // Mostrar cargando
    Swal.fire({
      title: "Verificando datos",
      text: "Espere un momento...",
      allowOutsideClick: false,
      didOpen: () => {
        Swal.showLoading();
      },
    });

    // Primero obtener los datos personales del usuario
    $.ajax({
      url: `/rrhh/datos_personal_por_dni/?dni=${dni}`,
      type: "GET",
      dataType: "json",
      success: function (personalResponse) {
        if (personalResponse.status === "success" && personalResponse.data) {
          // Si encontramos datos personales, verificar utilidades con el DNI
          $.ajax({
            url: `/rrhh/certificado_utilidades/?periodo=202604&factor=1&dni=${dni}`,
            type: "GET",
            dataType: "json",
            success: function (utilidadesResponse) {
              Swal.close();

              if (
                utilidadesResponse.status === "success" &&
                utilidadesResponse.data &&
                utilidadesResponse.data.length > 0
              ) {
                // Ya no necesitamos buscar por DNI en los resultados porque la API ya filtra
                // Tomamos el primer registro que viene de la consulta
                const usuarioConUtilidades = utilidadesResponse.data[0];

                if (usuarioConUtilidades) {
                  // Guardar los datos de utilidades para generar el PDF después
                  datosUtilidades = usuarioConUtilidades;
                  console.log("Datos para el PDF:", datosUtilidades);

                  // Antes de obtener los datos adicionales, solicitar la fecha de nacimiento
                  solicitarFechaNacimiento(dni);
                } else {
                  Swal.fire({
                    icon: "warning",
                    title: "No cuenta con utilidades",
                    text: "El usuario no tiene utilidades asignadas en el periodo actual. Por favor comuníquese con el área de Recursos Humanos para más información. Nota: Este proceso no aplica para trabajadores activos.",
                  });
                }
              } else {
                Swal.fire({
                  icon: "warning",
                  title: "No cuenta con utilidades",
                  text: "El usuario no tiene utilidades asignadas en el periodo actual. Por favor comuníquese con el área de Recursos Humanos para más información. Nota: Este proceso no aplica para trabajadores activos.",
                  confirmButtonText: "Entendido",
                });
              }
            },
            error: function (xhr, status, error) {
              Swal.close();
              console.error("Error al verificar utilidades:", error);
              Swal.fire({
                icon: "error",
                title: "Error",
                text: "Ocurrió un error al verificar las utilidades del usuario.",
                confirmButtonText: "Entendido",
              });
            },
          });
        } else {
          Swal.close();

          Swal.fire({
            icon: "warning",
            title: "Usuario no encontrado",
            text: "No se encontró información para el DNI proporcionado.",
            confirmButtonText: "Entendido",
          });
        }
      },
      error: function (xhr, status, error) {
        Swal.close();
        console.error("Error al buscar datos personales:", error);
        Swal.fire({
          icon: "error",
          title: "Error",
          text: "Ocurrió un error al buscar datos del usuario.",
          confirmButtonText: "Entendido",
        });
      },
    });
  }

  // Función para solicitar y validar la fecha de nacimiento (mejorada)
  function solicitarFechaNacimiento(dni) {
    // Reiniciar intentos si es una nueva consulta
    intentosValidacion = 0;

    // Función para validar y formatear la fecha
    function validarYFormatearFecha(entrada) {
      // Eliminar espacios y caracteres no numéricos
      let soloNumeros = entrada.replace(/[^\d]/g, "");

      // Verificar si tenemos exactamente 8 dígitos (DDMMAAAA)
      if (soloNumeros.length !== 8) {
        return {
          valido: false,
          mensaje: "La fecha debe tener 8 dígitos en formato DDMMAAAA",
        };
      }

      // Extraer día, mes y año
      let dia = soloNumeros.substring(0, 2);
      let mes = soloNumeros.substring(2, 4);
      let anio = soloNumeros.substring(4, 8);

      // Validaciones básicas
      let diaNum = parseInt(dia, 10);
      let mesNum = parseInt(mes, 10);
      let anioNum = parseInt(anio, 10);

      if (mesNum < 1 || mesNum > 12) {
        return {
          valido: false,
          mensaje: "El mes debe estar entre 01 y 12",
        };
      }

      // Días máximos según el mes
      let diasEnMes = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];

      // Ajustar febrero en años bisiestos
      if (
        mesNum === 2 &&
        ((anioNum % 4 === 0 && anioNum % 100 !== 0) || anioNum % 400 === 0)
      ) {
        diasEnMes[2] = 29;
      }

      if (diaNum < 1 || diaNum > diasEnMes[mesNum]) {
        return {
          valido: false,
          mensaje: `El día debe estar entre 01 y ${diasEnMes[mesNum]} para el mes ${mes}`,
        };
      }

      // Devolver la fecha formateada con separadores
      return {
        valido: true,
        fechaFormateada: `${dia}/${mes}/${anio}`,
      };
    }

    // Función para obtener la fecha de nacimiento real y validar
    function verificarFechaNacimiento(fechaIngresada) {
      // Mostrar loading
      Swal.fire({
        title: "Verificando identidad",
        text: "Espere un momento...",
        allowOutsideClick: false,
        didOpen: () => {
          Swal.showLoading();
        },
      });

      // Consultar fecha de nacimiento real
      $.ajax({
        url: `/rrhh/rrhh_personal_general/?dni=${dni}`,
        type: "GET",
        dataType: "json",
        success: function (response) {
          Swal.close();

          if (
            response.status === "success" &&
            response.data &&
            response.data.FECHA_NACIMIENTO
          ) {
            // Comparar con la fecha ingresada
            const fechaReal = response.data.FECHA_NACIMIENTO;

            if (fechaIngresada === fechaReal) {
              // Si es correcta, continuar con el flujo normal
              console.log("Validación exitosa - Identidad confirmada");
              obtenerDatosPersonal(dni);
            } else {
              // Si es incorrecta, incrementar contador y mostrar error
              intentosValidacion++;

              if (intentosValidacion >= MAX_INTENTOS) {
                Swal.fire({
                  icon: "error",
                  title: "Acceso denegado",
                  text: "Ha excedido el número máximo de intentos. Por motivos de seguridad, la consulta ha sido bloqueada.",
                  confirmButtonText: "Entendido",
                });

                // Limpiar el campo de DNI
                $("#searchInput").val("");
                datosUtilidades = null;
              } else {
                Swal.fire({
                  icon: "error",
                  title: "Fecha incorrecta",
                  text: `La fecha de nacimiento no coincide. Intento ${intentosValidacion} de ${MAX_INTENTOS}.`,
                  confirmButtonText: "Intentar nuevamente",
                }).then((result) => {
                  if (result.isConfirmed) {
                    // Volver a solicitar la fecha
                    mostrarFormularioFecha();
                  }
                });
              }
            }
          } else {
            Swal.fire({
              icon: "error",
              title: "Error de verificación",
              text: "No se pudo obtener la fecha de nacimiento para verificar su identidad.",
              confirmButtonText: "Entendido",
            });
          }
        },
        error: function (xhr, status, error) {
          Swal.close();
          console.error("Error al verificar fecha de nacimiento:", error);
          Swal.fire({
            icon: "error",
            title: "Error de verificación",
            text: "Ocurrió un error al verificar su identidad.",
            confirmButtonText: "Entendido",
          });
        },
      });
    }

    // Función para mostrar el formulario de fecha mejorado
    function mostrarFormularioFecha() {
      Swal.fire({
        title: "Verificación de identidad",
        html: `
          <div class="text-left">
            <p>Para proteger su información, por favor ingrese su fecha de nacimiento.</p>
            <p class="text-muted small">Puede ingresar la fecha con o sin separadores.</p>
            <div class="alert alert-info small" role="alert">
              <i class="fa fa-info-circle"></i> Ejemplos válidos:
              <ul class="mb-0 pl-3">
                <li>15/04/1990</li>
                <li>15041990</li>
              </ul>
            </div>
          </div>
        `,
        input: "text",
        inputPlaceholder: "Ejemplo: 15041990 o 15/04/1990",
        inputAttributes: {
          autocapitalize: "off",
          autocorrect: "off",
          maxlength: "10",
        },
        showCancelButton: true,
        confirmButtonText: "Verificar",
        cancelButtonText: "Cancelar",
        showLoaderOnConfirm: true,
        preConfirm: (inputFecha) => {
          if (!inputFecha) {
            Swal.showValidationMessage(
              "Por favor ingrese su fecha de nacimiento"
            );
            return false;
          }

          const resultado = validarYFormatearFecha(inputFecha);

          if (!resultado.valido) {
            Swal.showValidationMessage(resultado.mensaje);
            return false;
          }

          return resultado.fechaFormateada;
        },
        allowOutsideClick: () => !Swal.isLoading(),
      }).then((result) => {
        if (result.isConfirmed && result.value) {
          verificarFechaNacimiento(result.value);
        } else if (result.dismiss === Swal.DismissReason.cancel) {
          // Si cancela, limpiar el campo de DNI y datos
          $("#searchInput").val("");
          datosUtilidades = null;
        }
      });
    }

    // Iniciar el proceso mostrando el formulario de fecha
    mostrarFormularioFecha();
  }

  // Función para obtener datos personales adicionales
  function obtenerDatosPersonal(dni) {
    Swal.fire({
      title: "Obteniendo datos personales",
      text: "Espere un momento...",
      allowOutsideClick: false,
      didOpen: () => {
        Swal.showLoading();
      },
    });

    $.ajax({
      url: `/rrhh/rrhh_personal_general/?dni=${dni}`,
      type: "GET",
      dataType: "json",
      success: function (response) {
        Swal.close();

        if (response.status === "success" && response.data) {
          console.log("Datos personales obtenidos:", response.data);
          mostrarFormulario(response.data);
        } else {
          console.error(
            "Error al obtener datos personales adicionales:",
            response
          );
          // Aún así mostrar el formulario con los datos básicos
          mostrarFormulario({
            NOMBRES: "",
            DNI: dni,
            CELULAR: "",
            CORREO: "",
            idbanco: "",
            CUENTA_BANCO: "",
          });

          Swal.fire({
            icon: "warning",
            title: "Datos incompletos",
            text: "Se encontraron utilidades para el usuario, pero no se pudieron obtener todos sus datos personales.",
            confirmButtonText: "Entendido",
          });
        }
      },
      error: function (xhr, status, error) {
        Swal.close();
        console.error("Error al obtener datos personales adicionales:", error);

        // Aún así mostrar el formulario con los datos básicos
        mostrarFormulario({
          NOMBRES: "",
          DNI: dni,
          CELULAR: "",
          CORREO: "",
          idbanco: "",
          CUENTA_BANCO: "",
        });

        Swal.fire({
          icon: "warning",
          title: "Datos incompletos",
          text: "Se encontraron utilidades para el usuario, pero ocurrió un error al obtener sus datos personales.",
          confirmButtonText: "Entendido",
        });
      },
    });
  }

  // Función para mostrar el formulario con los datos del usuario
  function mostrarFormulario(userData) {
    // Llenar los campos del formulario con la información del usuario
    $('input[name="nombreCompleto"]').val(userData.NOMBRES || "");
    $('input[name="dni"]').val(userData.DNI || "");
    $('input[name="telefono"]').val(userData.CELULAR || "");
    $('input[name="email"]').val(userData.CORREO || "");
    $('input[name="numeroCuenta"]').val(userData.CUENTA_BANCO || "");
    $('input[name="cuentaInterbancaria"]').val(""); // Este campo no viene en la data

    // Seleccionar el banco correspondiente si está disponible
    if (userData.idbanco) {
      const bancoId = userData.idbanco.trim();
      $('select[name="banco"]').val(bancoId);

      // Si no se selecciona con el ID, intentar por nombre
      if (!$('select[name="banco"]').val()) {
        $('select[name="banco"] option').each(function () {
          if (
            $(this).val().toLowerCase() === bancoId.toLowerCase() ||
            $(this).text().toLowerCase().includes(bancoId.toLowerCase())
          ) {
            $(this).prop("selected", true);
            return false; // Salir del bucle una vez encontrado
          }
        });
      }
    }

    // Mostrar el formulario con una animación suave
    $("#userInfoForm").slideDown(300);

  }

  // Función para generar el PDF de certificado de utilidades
  function generarPDF(datos) {
    if (!datos) {
      console.error("No hay datos para generar el PDF");
      return false;
    }

    // Comprobar que jsPDF está disponible
    if (typeof jspdf === "undefined") {
      console.error("jsPDF no está disponible");
      Swal.fire({
        icon: "error",
        title: "Error",
        text: "No se pudo generar el PDF. La biblioteca jsPDF no está disponible.",
        confirmButtonText: "Entendido",
      });
      return false;
    }

    try {
      // Crear un nuevo documento PDF
      const { jsPDF } = jspdf;
      const doc = new jsPDF({
        orientation: "portrait",
        unit: "mm",
        format: "a4",
      });

      // Establecer fuente
      doc.setFont("helvetica");

      // Añadir logo
      try {
        const logoUrl = "/static/assets/img/logo/logo_dl.png"; // Ajustar ruta según corresponda
        doc.addImage(logoUrl, "PNG", 20, 10, 25, 25);
      } catch (e) {
        console.warn("No se pudo añadir el logo:", e);
      }

      // Encabezado
      doc.setFontSize(12);
      doc.setFont("helvetica", "bold");
      doc.text("SOCIEDAD AGRICOLA DON LUIS S.A.", 105, 15, { align: "center" });
      doc.setFontSize(8);
      doc.text("RUC : 20325346435", 105, 20, { align: "center" });
      doc.text(
        "DIRECCION: CAL. CONTRALMIRANTE MONTERO NRO. 411 INT. 404 URB.",
        105,
        25,
        { align: "center" }
      );
      doc.text("CAMPO DE POLO", 105, 30, { align: "center" });

      // Título
      doc.setFontSize(10);
      doc.text(
        "PARTICIPACION EN LAS UTILIDADES POR EL EJERCICIO GRAVABLE",
        105,
        40,
        { align: "center" }
      );
      doc.text(`AÑO ${datos.PERIODO}`, 105, 45, { align: "center" });

      // Datos personales
      doc.setFontSize(8);
      doc.setFont("helvetica", "bold");
      doc.text("APELLIDOS Y NOMBRES :", 20, 55);
      doc.text("DOC.IDENTIDAD N° :", 20, 60);

      doc.setFont("helvetica", "normal");
      doc.text(datos.APENOM, 70, 55);
      doc.text(datos.DNI, 70, 60);

      // Texto explicativo
      doc.setFontSize(7);
      doc.text(
        "El presente documento contiene el detalle del cálculo de la participación de Utilidades de acuerdo DL. N° 892",
        20,
        68
      );

      // Primer recuadro (tabla de detalles)
      doc.setLineWidth(0.3);
      doc.rect(20, 70, 170, 70); // Rectángulo exterior de la tabla

      // Encabezados y contenido de la primera tabla
      doc.setFontSize(7);
      let y = 75;
      const col1Width = 110;
      const col2Width = 10;
      const col3Width = 30;

      // Alineación a la derecha para las cifras
      const alignRight = function (text, x, y, width) {
        const textWidth =
          (doc.getStringUnitWidth(text) * 7) / doc.internal.scaleFactor;
        doc.text(text, x + width - textWidth - 2, y);
      };

      // Primera parte de la tabla
      doc.setFont("helvetica", "normal");
      doc.text("1. Participación a distribuir de la Renta Neta", 22, y);
      doc.text("S/.", col1Width + 22, y);
      alignRight(
        formatearNumero(datos.IMPORTE_REPARTIR),
        col1Width + col2Width + 22,
        y,
        col3Width
      );

      y += 8;
      doc.text(
        "2. Días laborados por todos los trabajadores en el año " +
          datos.PERIODO,
        22,
        y
      );
      alignRight(
        formatearNumero(datos.DIAS_TODOS),
        col1Width + col2Width + 22,
        y,
        col3Width
      );

      y += 8;
      doc.text(
        "3. Días laborados por el trabajador en el año " + datos.PERIODO,
        22,
        y
      );
      alignRight(
        formatearNumero(datos.DIAS_TRABAJADOR),
        col1Width + col2Width + 22,
        y,
        col3Width
      );

      y += 8;
      doc.text(
        "4. Remuneraciones percibidas por todos los trabajadores en el año " +
          datos.PERIODO,
        22,
        y
      );
      doc.text("S/.", col1Width + 22, y);
      alignRight(
        formatearNumero(datos.REMUNERACION_TODOS),
        col1Width + col2Width + 22,
        y,
        col3Width
      );

      y += 8;
      doc.text(
        "5. Remuneraciones percibidas por el trabajador en el año " +
          datos.PERIODO,
        22,
        y
      );
      doc.text("S/.", col1Width + 22, y);
      alignRight(
        formatearNumero(datos.REMUNERACION_TRABAJADOR),
        col1Width + col2Width + 22,
        y,
        col3Width
      );

      y += 8;
      doc.text(
        "6. A distribuir por los días laborados en el año " + datos.PERIODO,
        22,
        y
      );
      doc.text("S/.", col1Width + 22, y);
      alignRight(
        formatearNumero(datos.DISTRIBUIR_DIAS),
        col1Width + col2Width + 22,
        y,
        col3Width
      );

      y += 8;
      doc.text(
        "7. A distribuir por las remuneraciones percibidas en el año " +
          datos.PERIODO,
        22,
        y
      );
      doc.text("S/.", col1Width + 22, y);
      alignRight(
        formatearNumero(datos.DISTRIBUIR_REMUNERACION),
        col1Width + col2Width + 22,
        y,
        col3Width
      );

      // Segundo recuadro (liquidación)
      y = 150;
      doc.rect(20, y, 170, 70); // Rectángulo exterior de la segunda tabla

      // Título de liquidación
      doc.setFontSize(8);
      doc.setFont("helvetica", "bold");
      doc.text("LIQUIDACION DE LA PARTICIPACION DE UTILIDADES", 105, y + 7, {
        align: "center",
      });

      // Detalles de liquidación
      doc.setFontSize(7);
      doc.setFont("helvetica", "normal");
      y += 15;

      // Agregar las filas de la liquidación
      doc.text(
        `1. Por     ${
          datos.DIAS_TRABAJADOR
        } día(s) laborados (${formatearNumero(datos.DISTRIBUIR_DIAS)} × ${
          datos.DIAS_TRABAJADOR
        } / ${formatearNumero(datos.DIAS_TODOS)})`,
        22,
        y
      );
      doc.text("S/.", col1Width + 22, y);
      alignRight(
        formatearNumero(datos.INGRESO_XDIA),
        col1Width + col2Width + 22,
        y,
        col3Width
      );

      y += 8;
      doc.text(
        `2. Por S/.  ${formatearNumero(
          datos.REMUNERACION_TRABAJADOR
        )} de remuneraciones percibidas (${formatearNumero(
          datos.DISTRIBUIR_REMUNERACION
        )} × ${formatearNumero(
          datos.REMUNERACION_TRABAJADOR
        )} / ${formatearNumero(datos.REMUNERACION_TODOS)})`,
        22,
        y
      );
      doc.text("S/.", col1Width + 22, y);
      alignRight(
        formatearNumero(datos.INGRESO_XREMUNE),
        col1Width + col2Width + 22,
        y,
        col3Width
      );

      y += 8;
      doc.text("3. Por     Retención de Renta de Quinta Categoría", 22, y);
      doc.text("S/.", col1Width + 22, y);
      alignRight(
        formatearNumero(datos.RENTA || "0.00"),
        col1Width + col2Width + 22,
        y,
        col3Width
      );

      y += 8;
      doc.text("4. Por     Adelanto de Utilidades", 22, y);
      doc.text("S/.", col1Width + 22, y);
      alignRight(
        formatearNumero(datos.DSCTO_ADELUTIL || "0.00"),
        col1Width + col2Width + 22,
        y,
        col3Width
      );

      y += 12;
      doc.setFont("helvetica", "bold");
      doc.text("NETO PAGADO", 80, y);
      doc.text("S/.", col1Width + 22, y);
      alignRight(
        formatearNumero(datos.UTILIDAD_NETA),
        col1Width + col2Width + 22,
        y,
        col3Width
      );

      // Texto de conformidad
      y += 10;
      doc.setFontSize(6);
      doc.setFont("helvetica", "normal");
      const textoConformidad =
        "Por el presente declaro estar conforme con la presente liquidación de participación de utilidades del periodo " +
        datos.PERIODO +
        " la misma que recibo en señal de aceptación y plena conformidad, ya que la misma ha sido revisada por " +
        "mi persona, no teniendo motivo o concepto por el cual reclamar";

      const lineas = doc.splitTextToSize(textoConformidad, 160);
      doc.text(lineas, 22, y);

      // Fecha
      y += 15;
      const fechaActual = new Date();
      const dia = fechaActual.getDate();
      const mes = fechaActual.getMonth() + 1;
      const año = fechaActual.getFullYear();
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
      doc.text(`Ica, ${dia} de ${meses[mes - 1]} del ${año}`, 105, y, {
        align: "center",
      });

      // Firmas
      y += 20;
      doc.line(40, y, 80, y); // Línea para firma empleador
      doc.line(120, y, 160, y); // Línea para firma trabajador

      // Nombre del jefe de RRHH
      doc.setFontSize(6);

      /* doc.text("INDIRA MARIA QUISPE YLLANEZ", 60, y + 5, { align: "center" });
      doc.text("JEFE DE RECURSOS HUMANOS", 60, y + 9, { align: "center" });
     */
      // Etiquetas EMPLEADOR y TRABAJADOR
      doc.text("EMPLEADOR", 60, y + 5, { align: "center" });
      doc.text("TRABAJADOR", 140, y + 5, { align: "center" });

      // Logo de la empresa en la parte inferior (si hay espacio)
      try {
        doc.setDrawColor(0);
        doc.setFillColor(255, 255, 255);
        doc.setLineWidth(0.1);

        // Añadir la imagen de la firma donde está marcado en rojo
        try {
          const firmaUrl = "/static/img/firma_iquispe.png"; // Ajusta la ruta según corresponda
          // Posicionar la firma sobre la línea del EMPLEADOR (aproximadamente donde está el cuadro rojo)
          doc.addImage(firmaUrl, "PNG", 40, y - 15, 40, 15);
        } catch (e) {
          console.warn("No se pudo añadir la imagen de la firma:", e);
        }

        // Añadir textos de identificación
        /* doc.text("INDIRA MARIA QUISPE YLLANEZ", 60, y + 5, { align: "center" });
        doc.text("JEFE DE RECURSOS HUMANOS", 60, y + 9, { align: "center" });
       */
        // Añadir textos "EMPLEADOR" y "TRABAJADOR"
        /* doc.text("EMPLEADOR", 60, y + 20, { align: "center" });
        doc.text("TRABAJADOR", 140, y + 20, { align: "center" }); */

        // Añadir SOCIEDAD AGRICOLA DON LUIS como sello
        try {
          const selloUrl = "/static/assets/img/logo/firma_iquispe.png"; // Ajusta la ruta según corresponda
          // Posicionar el sello justo encima de la línea de la firma
          doc.addImage(selloUrl, "PNG", 40, y - 17, 40, 15);
        } catch (e) {
          console.warn("No se pudo añadir la imagen del sello:", e);
          // Si no se puede cargar la imagen, usar texto como respaldo
          doc.setFontSize(5);
          doc.text("SOCIEDAD AGRICOLA DON LUIS S.A.", 60, y - 5, {
            align: "center",
          });
          doc.text("RUC 20325346435", 60, y - 2, { align: "center" });
        }
      } catch (e) {
        console.warn("Error al agregar elementos adicionales:", e);
      }

      // Crear blob y URL del PDF para visor o descarga directa
      const pdfBlob = doc.output("blob");
      const pdfUrl = URL.createObjectURL(pdfBlob);

      // Determinar si estamos en un dispositivo móvil
      const esMobile = window.matchMedia("(max-width: 767px)").matches;

      // En dispositivos móviles, ofrecer descarga directa en Safari/iOS
      const esIOS =
        /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
      const esSafari = /^((?!chrome|android).)*safari/i.test(
        navigator.userAgent
      );

      if (esMobile && (esIOS || esSafari)) {
        // En iOS/Safari, crear un enlace y hacer clic en él
        const filename = `Certificado_Utilidades_${datos.DNI}_${datos.PERIODO}.pdf`;
        // Guardar directamente para Safari/iOS
        window.location.href = pdfUrl;

        // Informar al usuario
        Swal.fire({
          icon: "success",
          title: "Descargando PDF",
          text: "El certificado se está descargando automáticamente",
          timer: 3000,
          timerProgressBar: true,
        });

        // Limpiar el blob después de un tiempo
        setTimeout(() => {
          URL.revokeObjectURL(pdfUrl);
        }, 5000);

        return true;
      }

      // Para otros dispositivos, usar el visor de PDF
      try {
        // Mostrar el PDF en el modal
        const viewer = document.getElementById("pdfViewer");

        // Verificar que PDFObject está disponible
        if (typeof PDFObject === "undefined") {
          throw new Error("PDFObject no está disponible");
        }

        // Limpiar el contenedor antes de embeber nuevo PDF
        viewer.innerHTML = "";

        // Intentar embeber el PDF
        const pdfEmbedded = PDFObject.embed(pdfUrl, viewer);

        // Verificar si se pudo embeber
        if (!pdfEmbedded) {
          throw new Error("No se pudo embeber el PDF");
        }

        // Mostrar el modal
        $("#pdfModal").modal("show");

        // Manejar el botón de descarga
        $("#btnDescargarPDF")
          .off("click")
          .on("click", function () {
            const filename = `Certificado_Utilidades_${datos.DNI}_${datos.PERIODO}.pdf`;
            doc.save(filename);
          });

        // Limpiar el blob cuando se cierre el modal
        $("#pdfModal").on("hidden.bs.modal", function () {
          URL.revokeObjectURL(pdfUrl);
        });

        return true;
      } catch (error) {
        console.error("Error al mostrar el PDF en el visor:", error);

        // Si falla el visor, ofrecer descarga directa
        const filename = `Certificado_Utilidades_${datos.DNI}_${datos.PERIODO}.pdf`;
        doc.save(filename);

        Swal.fire({
          icon: "info",
          title: "Descarga directa",
          text: "La constancia se ha descargado directamente debido a un problema con el visor.",
          confirmButtonText: "Entendido",
        });

        return true;
      }
    } catch (e) {
      console.error("Error general al generar el PDF:", e);
      Swal.fire({
        icon: "error",
        title: "Error",
        text: "Ocurrió un error al generar el constancia. Por favor, intente nuevamente.",
        confirmButtonText: "Entendido",
      });
      return false;
    }
  }

  // Función para formatear números con separadores de miles y dos decimales
  function formatearNumero(numero) {
    if (!numero) return "0.00";

    const num = parseFloat(numero);
    return num.toLocaleString("es-PE", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    });
  }

  // Event listener para el campo de búsqueda (keypress en Enter)
  $("#searchInput").keypress(function (e) {
    if (e.which === 13) {
      // Tecla Enter
      const dni = $(this).val().trim();
      if (dni.length > 0) {
        verificarUtilidades(dni);
      } else {
        Swal.fire({
          icon: "warning",
          title: "Campo vacío",
          text: "Por favor, ingrese un número de DNI.",
          confirmButtonText: "Entendido",
        });
      }
    }
  });

  // Event listener para cambios en el campo de DNI (para verificar automáticamente)
  $("#searchInput").on("input", function () {
    const dni = $(this).val().trim();
    // Verificar si el DNI tiene 8 dígitos (estándar en Perú)
    if (dni.length === 8 && /^\d+$/.test(dni)) {
      verificarUtilidades(dni);
    }
  });

  // Modificar el manejo del envío del formulario
  $("#userInfoForm").submit(function (e) {
    e.preventDefault();

    // Validar campos requeridos
    let isValid = true;
    const camposRequeridos = ["telefono", "email", "banco", "numeroCuenta"];

    camposRequeridos.forEach(function (campo) {
      const valor = $(`[name="${campo}"]`).val();
      if (!valor || valor.trim() === "") {
        isValid = false;
        $(`[name="${campo}"]`).addClass("is-invalid");
      } else {
        $(`[name="${campo}"]`).removeClass("is-invalid");
      }
    });

    if (!isValid) {
      Swal.fire({
        icon: "error",
        title: "Campos requeridos",
        text: "Por favor complete todos los campos obligatorios.",
        confirmButtonText: "Entendido",
      });
      return;
    }

    // Recopilar los datos del formulario
    const formData = {
      dni: $('input[name="dni"]').val(),
      telefono: $('input[name="telefono"]').val(),
      email: $('input[name="email"]').val(),
      banco: $('select[name="banco"]').val(),
      numeroCuenta: $('input[name="numeroCuenta"]').val(),
      cuentaInterbancaria: $('input[name="cuentaInterbancaria"]').val(),
      periodo: "2026",
    };

    // Mostrar resumen de datos antes de guardar
    const bancoSeleccionado = $('select[name="banco"] option:selected').text();

    Swal.fire({
      title: "¿Los datos son correctos?",
      html: `
            <div class="text-left">
                <p class="mb-2"><strong>DNI:</strong> ${formData.dni}</p>
                <p class="mb-2"><strong>Teléfono:</strong> ${formData.telefono}</p>
                <p class="mb-2"><strong>Email:</strong> ${formData.email}</p>
                <p class="mb-2"><strong>Banco:</strong> ${bancoSeleccionado}</p>
                <p class="mb-2"><strong>N° Cuenta:</strong> ${formData.numeroCuenta}</p>
                <p class="mb-2"><strong>Cuenta Interbancaria:</strong> ${formData.cuentaInterbancaria}</p>
            </div>
            <div class="alert alert-warning mt-3 mb-0" role="alert">
                <i class="fa fa-exclamation-triangle"></i>
                Por favor, verifique que todos los datos sean correctos antes de guardar.
                <br>
                <small>Una vez guardados, estos datos serán utilizados para el pago de sus utilidades.</small>
            </div>
        `,
      icon: "warning",
      showCancelButton: true,
      confirmButtonColor: "#3085d6",
      cancelButtonColor: "#d33",
      confirmButtonText: "Sí, guardar datos",
      cancelButtonText: "No, revisar datos",
      reverseButtons: true,
    }).then((result) => {
      if (result.isConfirmed) {
        // Mostrar cargando
        Swal.fire({
          title: "Guardando datos",
          text: "Espere un momento...",
          allowOutsideClick: false,
          didOpen: () => {
            Swal.showLoading();
          },
        });

        // Enviar datos al servidor
        $.ajax({
          url: "/rrhh/utilidades_empleados/",
          type: "POST",
          contentType: "application/json",
          data: JSON.stringify(formData),
          success: function (response) {
            Swal.close();

            if (response.status === "success") {
              // Limpiar y ocultar el formulario
              $("#userInfoForm")[0].reset();
              $("#userInfoForm").slideUp(300);

              // Limpiar el campo de búsqueda
              $("#searchInput").val("");

              Swal.fire({
                icon: "success",
                title: "Guardado exitoso",
                text: response.message,
                confirmButtonText: "Ver Constancia",
                showCancelButton: true,
                cancelButtonText: "Cerrar",
              }).then((result) => {
                if (result.isConfirmed && datosUtilidades) {
                  try {
                    generarPDF(datosUtilidades);
                  } catch (error) {
                    console.error("Error al generar el PDF:", error);
                    Swal.fire({
                      icon: "error",
                      title: "Error",
                      text: "No se pudo generar el certificado PDF. Por favor, intente de nuevo más tarde.",
                      confirmButtonText: "Entendido",
                    });
                  }
                }
                // Después de cerrar el SweetAlert, limpiar los datos de utilidades
                datosUtilidades = null;
              });
            } else {
              Swal.fire({
                icon: "error",
                title: "Error",
                text:
                  response.message || "Ocurrió un error al guardar los datos.",
                confirmButtonText: "Entendido",
              });
            }
          },
          error: function (xhr, status, error) {
            Swal.close();

            console.error("Error al guardar datos:", error);
            let errorMessage = "Ocurrió un error al guardar los datos.";

            if (xhr.responseJSON && xhr.responseJSON.message) {
              errorMessage = xhr.responseJSON.message;
            }

            Swal.fire({
              icon: "error",
              title: "Error",
              text: errorMessage,
              confirmButtonText: "Entendido",
            });
          },
        });
      }
    });
  });

  // Event listener para botón de descarga
  $("#btnDescargarCertificado").click(function () {
    if (datosUtilidades) {
      try {
        generarPDF(datosUtilidades);
      } catch (error) {
        console.error("Error al generar el PDF:", error);
        Swal.fire({
          icon: "error",
          title: "Error",
          text: "No se pudo generar el certificado PDF. Por favor, intente de nuevo más tarde.",
          confirmButtonText: "Entendido",
        });
      }
    } else {
      Swal.fire({
        icon: "warning",
        title: "No hay datos disponibles",
        text: "Primero debe buscar un usuario con utilidades para poder descargar el constancia.",
        confirmButtonText: "Entendido",
      });
    }
  });

  // Manejar el botón Cancelar
  $("button.btn-white").click(function () {
    // Limpiar el formulario
    $("#userInfoForm")[0].reset();
    // Ocultar el formulario con animación
    $("#userInfoForm").slideUp(300);
    // Limpiar el campo de búsqueda
    $("#searchInput").val("");
    // Limpiar los datos de utilidades
    datosUtilidades = null;
  });

  // Modificar el event listener del modal PDF para limpiar datos cuando se cierre
  $("#pdfModal").on("hidden.bs.modal", function () {
    URL.revokeObjectURL(pdfUrl);
    // No limpiar datosUtilidades aquí para permitir múltiples visualizaciones
  });
});
