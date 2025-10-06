document.addEventListener("DOMContentLoaded", () => {
  const btnGuardar = document.getElementById("guardarPeriodos");
  const confirmBtn = document.getElementById("confirmGuardar");
  const modalEl = document.getElementById("confirmModal");

  // 👉 Al cargar la página, recuperar datos de localStorage
  const datosGuardados = JSON.parse(localStorage.getItem("fechasPeriodos"));
  if (datosGuardados) {
    document.getElementById("p1_inicio").value = datosGuardados.p1.inicio;
    document.getElementById("p1_fin").value = datosGuardados.p1.fin;
    document.getElementById("p2_inicio").value = datosGuardados.p2.inicio;
    document.getElementById("p2_fin").value = datosGuardados.p2.fin;
    document.getElementById("p3_inicio").value = datosGuardados.p3.inicio;
    document.getElementById("p3_fin").value = datosGuardados.p3.fin;
    document.getElementById("p4_inicio").value = datosGuardados.p4.inicio;
    document.getElementById("p4_fin").value = datosGuardados.p4.fin;

    // También mostrar en el resumen
    document.getElementById("resumen_p1").innerHTML = `<div class="mini-barra">Inicio ${datosGuardados.p1.inicio} - Fin ${datosGuardados.p1.fin}</div>`;
    document.getElementById("resumen_p2").innerHTML = `<div class="mini-barra">Inicio ${datosGuardados.p2.inicio} - Fin ${datosGuardados.p2.fin}</div>`;
    document.getElementById("resumen_p3").innerHTML = `<div class="mini-barra">Inicio ${datosGuardados.p3.inicio} - Fin ${datosGuardados.p3.fin}</div>`;
    document.getElementById("resumen_p4").innerHTML = `<div class="mini-barra">Inicio ${datosGuardados.p4.inicio} - Fin ${datosGuardados.p4.fin}</div>`;
  }

  btnGuardar.addEventListener("click", () => {
    let inputs = document.querySelectorAll(".periodos-card input[type='date']");
    let incompletos = [];

    inputs.forEach((inp) => {
      if (!inp.value) incompletos.push(inp);
    });

    if (incompletos.length > 0) {
      alert("⚠️ No puedes guardar. Faltan fechas por completar.");
      return;
    }

    let modal = new bootstrap.Modal(modalEl);
    modal.show();
  });

  confirmBtn.addEventListener("click", () => {
    // Obtener datos
    let datos = {
      p1: { inicio: document.getElementById("p1_inicio").value, fin: document.getElementById("p1_fin").value },
      p2: { inicio: document.getElementById("p2_inicio").value, fin: document.getElementById("p2_fin").value },
      p3: { inicio: document.getElementById("p3_inicio").value, fin: document.getElementById("p3_fin").value },
      p4: { inicio: document.getElementById("p4_inicio").value, fin: document.getElementById("p4_fin").value },
    };

    console.log("✅ Fechas guardadas:", datos);

    // 👉 Guardar en localStorage
    localStorage.setItem("fechasPeriodos", JSON.stringify(datos));

    // Cerrar modal
    let modal = bootstrap.Modal.getInstance(modalEl);
    if (modal) modal.hide();

    // Insertar cada registro debajo del periodo correspondiente
    document.getElementById("resumen_p1").innerHTML = `<div class="mini-barra">Inicio ${datos.p1.inicio} - Fin ${datos.p1.fin}</div>`;
    document.getElementById("resumen_p2").innerHTML = `<div class="mini-barra">Inicio ${datos.p2.inicio} - Fin ${datos.p2.fin}</div>`;
    document.getElementById("resumen_p3").innerHTML = `<div class="mini-barra">Inicio ${datos.p3.inicio} - Fin ${datos.p3.fin}</div>`;
    document.getElementById("resumen_p4").innerHTML = `<div class="mini-barra">Inicio ${datos.p4.inicio} - Fin ${datos.p4.fin}</div>`;

    alert("✅ Fechas de periodos guardadas correctamente");
  });
});
