let notasGuardadas = [];

// Guarda una copia exacta de lo que hay actualmente
function guardarSnapshot() {
  const inputs = document.querySelectorAll(".tabla input, .tabla select");
  notasGuardadas = Array.from(inputs).map(el => el.value);
}

// Guardar notas
function guardarNotas() {
  const inputs = document.querySelectorAll(".tabla input, .tabla select");

  const algunLleno = Array.from(inputs).some(el => el.value.trim() !== "");
  if (!algunLleno) {
    alert("⚠️ Debes llenar al menos un campo antes de guardar.");
    return;
  }

  for (let input of inputs) {
    if (input.type === "number" && input.value !== "") {
      const val = parseFloat(input.value);
      if (val < 1 || val > 5) {
        alert("⚠️ Todas las notas deben estar entre 1.0 y 5.0");
        return;
      }
    }
  }

  guardarSnapshot(); // aquí se guarda el "último estado válido"

  alert("✅ Notas guardadas correctamente.");
}

// Restablecer al último guardado
function restablecerNotas() {
  const inputs = document.querySelectorAll(".tabla input, .tabla select");
  inputs.forEach((el, idx) => {
    // si existe snapshot, lo ponemos; si no, se queda como estaba
    if (notasGuardadas[idx] !== undefined) {
      el.value = notasGuardadas[idx];
    }
  });
  alert("↩️ Notas restablecidas al último guardado.");
}
