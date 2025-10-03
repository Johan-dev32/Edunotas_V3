document.addEventListener("DOMContentLoaded", () => {
  const btnGuardar = document.getElementById("guardarPeriodos");
  const confirmBtn = document.getElementById("confirmGuardar");
  const modalEl = document.getElementById("confirmModal");

  btnGuardar.addEventListener("click", () => {
    // Obtener todos los inputs de tipo fecha
    let inputs = document.querySelectorAll(".periodos-card input[type='date']");
    let incompletos = [];

    inputs.forEach((inp) => {
      if (!inp.value) {
        incompletos.push(inp);
      }
    });

    if (incompletos.length > 0) {
      // Si hay fechas vacías mostramos un aviso
      alert("⚠️ No puedes guardar. Faltan fechas por completar.");
      return;
    }

    // Si todo está completo abrimos el modal
    let modal = new bootstrap.Modal(modalEl);
    modal.show();
  });

  // Acción cuando se confirma el guardado
  confirmBtn.addEventListener("click", () => {
    let datos = {
      p1: { inicio: document.getElementById("p1_inicio").value, fin: document.getElementById("p1_fin").value },
      p2: { inicio: document.getElementById("p2_inicio").value, fin: document.getElementById("p2_fin").value },
      p3: { inicio: document.getElementById("p3_inicio").value, fin: document.getElementById("p3_fin").value },
      p4: { inicio: document.getElementById("p4_inicio").value, fin: document.getElementById("p4_fin").value },
    };

    console.log("✅ Fechas guardadas:", datos);

    // Cerrar modal
    let modal = bootstrap.Modal.getInstance(modalEl);
    if (modal) modal.hide();

    // Aviso de éxito
    alert("✅ Fechas de periodos guardadas correctamente");
  });
});
