// ================================
// CONFIGURACIÓN
// ================================

// Número fijo de WhatsApp (cámbialo si quieres)
const NUMERO_ADMIN = "573229310911";

// ================================
// FUNCIONALIDAD PRINCIPAL
// ================================

document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector("form");
  const historyBody = document.getElementById("historyBody");

  // Cargar historial guardado
  cargarHistorial();

  // Enviar por WhatsApp
  form.addEventListener("submit", (e) => {
    e.preventDefault();

    const curso = document.getElementById("courseSelect").value;
    const tipo = document.getElementById("tipoMensaje").value;
    const archivo = document.getElementById("fileInput").value.split("\\").pop();

    if (!curso || !tipo || !archivo) {
      alert("Por favor completa todos los campos.");
      return;
    }

    // Crear mensaje
    const mensaje = `📢 *${tipo}*\n\nCurso: ${curso}\nArchivo: ${archivo}\n\nEnviado desde *EduNotas*`;

    // Abrir WhatsApp al número fijo
    const url = `https://wa.me/${NUMERO_ADMIN}?text=${encodeURIComponent(mensaje)}`;
    window.open(url, "_blank");

    // Guardar en historial
    guardarEnHistorial({
      archivo,
      curso,
      tipo,
      fecha: new Date().toLocaleString(),
      estado: "Enviado ✅",
    });

    // Limpiar formulario
    form.reset();
  });

  // ================================
  // FUNCIONES DE HISTORIAL
  // ================================

  function guardarEnHistorial(item) {
    const historial = JSON.parse(localStorage.getItem("historialEnvios")) || [];
    historial.push(item);
    localStorage.setItem("historialEnvios", JSON.stringify(historial));
    agregarFila(item);
  }

  function cargarHistorial() {
    const historial = JSON.parse(localStorage.getItem("historialEnvios")) || [];
    historyBody.innerHTML = "";
    historial.forEach((item) => agregarFila(item));
  }

  function agregarFila(item) {
    const fila = document.createElement("tr");
    fila.innerHTML = `
      <td>${item.archivo}</td>
      <td>${item.curso}</td>
      <td>${item.tipo}</td>
      <td>${item.fecha}</td>
      <td>${item.estado}</td>
    `;
    historyBody.appendChild(fila);
  }
});
