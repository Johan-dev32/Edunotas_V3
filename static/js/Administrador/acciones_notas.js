let notasGuardadas = [];

// Guarda el estado actual (snapshot)
function guardarSnapshot() {
  const inputs = document.querySelectorAll("table input, table select");
  notasGuardadas = Array.from(inputs).map(el => el.value);
}

// Guardar notas
function guardarNotas() {
  const filas = document.querySelectorAll("table tbody tr");
  if (filas.length === 0) {
    alert("⚠️ No hay filas para guardar.");
    return;
  }

  const datos = [];
  let algunLleno = false;

  filas.forEach(fila => {
    const inputs = fila.querySelectorAll("input, select");
    const filaDatos = {};

    inputs.forEach(input => {
      filaDatos[input.name] = input.value.trim();
      if (input.value.trim() !== "") algunLleno = true;
    });

    datos.push(filaDatos);
  });

  // Validación: al menos un campo lleno
  if (!algunLleno) {
    alert("⚠️ Debes llenar al menos un campo antes de guardar.");
    return;
  }

  // Validar solo notas numéricas llenas
  for (let fila of datos) {
    for (let [key, val] of Object.entries(fila)) {
      if (key.startsWith("nota") && val !== "") {
        const num = parseFloat(val);
        if (isNaN(num) || num < 1 || num > 5) {
          alert("⚠️ Las notas deben estar entre 1.0 y 5.0");
          return;
        }
      }
    }
  }

  // Guardar snapshot local (simula guardado correcto)
  guardarSnapshot();

  // Simular envío a servidor (más adelante aquí se usará fetch)
  console.log("Datos preparados para enviar a BD:", datos);

  alert("✅ Notas guardadas correctamente (modo local por ahora).");
}

// Restablecer notas
function restablecerNotas() {
  const inputs = document.querySelectorAll("table input, table select");

  if (notasGuardadas.length === 0) {
    alert("⚠️ No hay un guardado previo para restablecer.");
    return;
  }

  inputs.forEach((el, idx) => {
    if (notasGuardadas[idx] !== undefined) {
      el.value = notasGuardadas[idx];
    }
  });

  alert("↩️ Notas restablecidas al último guardado.");
}
