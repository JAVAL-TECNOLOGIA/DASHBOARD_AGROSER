function getCampaniaActual() {
  // Buscar el select de campaña (puede ser cmbCampania o filtroAnioPresupuesto)
  const cmb = document.getElementById("filtroAnioPresupuesto") || document.getElementById("cmbCampania");
  return cmb ? cmb.value : null; // ej: CAMP2025
}

// 1) Agrega ?year=... a todo $.ajax GET de /produccionuva1/
// 2) Agrega ID_CAMPANIA al body de todo $.ajax POST de /produccionuva1/
$.ajaxPrefilter(function (options, originalOptions, jqXHR) {
  if (!options.url) return;
  if (!options.url.startsWith("/produccionuva1/")) return;

  const camp = getCampaniaActual();
  if (!camp) return;

  // Para peticiones GET: agregar year como query param
  if (!options.type || options.type.toUpperCase() === "GET") {
    // Evita duplicar si ya tiene year= o campania=
    if (options.url.includes("year=") || options.url.includes("campania=")) return;
    const sep = options.url.includes("?") ? "&" : "?";
    options.url = options.url + sep + "year=" + encodeURIComponent(camp);
  }
  
  // Para peticiones POST/PUT: agregar ID_CAMPANIA al body JSON
  if (options.type && (options.type.toUpperCase() === "POST" || options.type.toUpperCase() === "PUT")) {
    // Si el contentType es JSON y data es un string (ya stringificado)
    if (options.contentType && options.contentType.includes("application/json") && typeof options.data === "string") {
      try {
        var jsonData = JSON.parse(options.data);
        if (!jsonData.ID_CAMPANIA) {
          jsonData.ID_CAMPANIA = camp;
          options.data = JSON.stringify(jsonData);
        }
      } catch (e) {
        console.log("Error parsing JSON for campaign injection:", e);
      }
    }
    // Si el data es un string (form serializado)
    else if (typeof options.data === "string" && !options.contentType) {
      if (!options.data.includes("ID_CAMPANIA=")) {
        options.data += (options.data ? "&" : "") + "ID_CAMPANIA=" + encodeURIComponent(camp);
      }
    }
    // Si el data es un objeto
    else if (typeof options.data === "object" && options.data !== null) {
      if (!options.data.ID_CAMPANIA) {
        options.data.ID_CAMPANIA = camp;
      }
    }
  }
});
