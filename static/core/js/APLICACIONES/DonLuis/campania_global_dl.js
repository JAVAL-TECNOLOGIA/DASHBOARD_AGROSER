function getCampaniaActual() {
  // Buscar el select de campaña (puede ser cmbCampania o filtroAnioPresupuesto)
  const cmb = document.getElementById("filtroAnioPresupuesto") || document.getElementById("cmbCampania");
  return cmb ? cmb.value : null; // ej: CAMP2025
}

// Agrega ?year=... a todo $.ajax GET de /aplicaciones/
// Agrega ID_CAMPANIA al body de todo $.ajax POST/PUT de /aplicaciones/
$.ajaxPrefilter(function (options, originalOptions, jqXHR) {
  if (!options.url) return;
  if (!options.url.startsWith("/aplicaciones/")) return;

  const camp = getCampaniaActual();
  if (!camp) return;

  // Para peticiones GET: agregar year como query param
  if (!options.type || options.type.toUpperCase() === "GET") {
    // Evita duplicar si ya tiene year= o ID_CAMPANIA=
    if (options.url.includes("year=") || options.url.includes("ID_CAMPANIA=")) return;
    const sep = options.url.includes("?") ? "&" : "?";
    options.url = options.url + sep + "year=" + encodeURIComponent(camp);
  }
  
  // Para peticiones POST/PUT: agregar ID_CAMPANIA al body
  if (options.type && (options.type.toUpperCase() === "POST" || options.type.toUpperCase() === "PUT")) {
    // Si el data es un string (form serializado o JSON), agregar ID_CAMPANIA
    if (typeof options.data === "string") {
      // Si es JSON string, parsearlo, agregar ID_CAMPANIA y volver a stringify
      if (options.contentType && options.contentType.includes("application/json")&& typeof options.data === "string") {
        try {
          const dataObj = JSON.parse(options.data);
          if (!dataObj.ID_CAMPANIA) {
            dataObj.ID_CAMPANIA = camp;
            options.data = JSON.stringify(dataObj);
          }
        } catch (e) {
        console.log("Error parsing JSON for campaign injection:", e);
      }
      } 
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
  }
});
