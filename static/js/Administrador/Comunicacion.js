// Cursos de 601 a 1103
const courses = [];

for (let grade = 6; grade <= 11; grade++) {
  for (let section = 1; section <= 3; section++) {
    const id = `${grade}0${section}`;  // 601, 602, 603, etc.
    const name = `${id} - ${String.fromCharCode(64 + section)}`; // A, B, C
    courses.push({ id, name });
  }
}


// Enlaces por curso
const groupLinks = {
  '601': 'https://web.whatsapp.com/send?text=Grupo%20601',
  '602': 'https://web.whatsapp.com/send?text=Grupo%20602',
  '603': 'https://web.whatsapp.com/send?text=Grupo%20603',
  '701': 'https://web.whatsapp.com/send?text=Grupo%20701',
  '702': 'https://web.whatsapp.com/send?text=Grupo%20702',
  '703': 'https://web.whatsapp.com/send?text=Grupo%20703',
  '801': 'https://web.whatsapp.com/send?text=Grupo%20801',
  '802': 'https://web.whatsapp.com/send?text=Grupo%20802',
  '803': 'https://web.whatsapp.com/send?text=Grupo%20803',
  '901': 'https://web.whatsapp.com/send?text=Grupo%20901',
  '902': 'https://web.whatsapp.com/send?text=Grupo%20902',
  '903': 'https://web.whatsapp.com/send?text=Grupo%20903',
  '1001': 'https://web.whatsapp.com/send?text=Grupo%201001',
  '1002': 'https://web.whatsapp.com/send?text=Grupo%201002',
  '1003': 'https://web.whatsapp.com/send?text=Grupo%201003',
  '1101': 'https://web.whatsapp.com/send?text=Grupo%201101',
  '1102': 'https://web.whatsapp.com/send?text=Grupo%201102',
  '1103': 'https://web.whatsapp.com/send?text=Grupo%201103',
  // Puedes completar hasta 1103...
};

let selectedType = null;
let selectedCourseId = null;
let selectedFile = null;

const $ = id => document.getElementById(id);

document.addEventListener("DOMContentLoaded", () => {
  const courseSelect = $("courseSelect");
  const sendBtn = $("sendBtn");
  const clearBtn = $("clearBtn");
  const feedback = $("feedback");
  const typeRow = $("typeRow");
  const fileBox = $("fileBox");
  const fileInput = $("fileInput");
  const fileNameEl = $("fileName");
  const confirmModal = $("confirmModal");
  const confirmText = $("confirmText");
  const cancelSend = $("cancelSend");
  const confirmSend = $("confirmSend");

  // (Opcional) modal de éxito eliminado
  // const successModal = $("successModal");
  // const successText = $("successText");
  // const closeSuccess = $("closeSuccess");

  // Cargar cursos al <select>
  courses.forEach(c => {
    const opt = document.createElement("option");
    opt.value = c.id;
    opt.textContent = c.name;
    courseSelect.appendChild(opt);
  });

  // Evento: selección de curso
  courseSelect.addEventListener("change", () => {
    selectedCourseId = courseSelect.value;
    updateControls();
  });

  // Evento: tipo de mensaje
  typeRow.querySelectorAll(".btn-type").forEach(btn => {
    btn.addEventListener("click", () => {
      typeRow.querySelectorAll(".btn-type").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      selectedType = btn.dataset.type;
      updateControls();
    });
  });

  // Evento: selección de archivo
  fileBox.addEventListener("click", () => fileInput.click());
  fileInput.addEventListener("change", e => {
    const file = e.target.files[0];
    if (file) {
      selectedFile = file;
      fileNameEl.textContent = file.name;
    }
  });

  // Mostrar modal de confirmación
  sendBtn.addEventListener("click", () => {
    if (!selectedCourseId || !selectedType) {
      feedback.textContent = "Selecciona curso y tipo";
      return;
    }
    const courseName = courses.find(c => c.id === selectedCourseId)?.name || selectedCourseId;
    confirmText.textContent = `Vas a enviar al curso ${courseName} como "${selectedType}". ¿Deseas continuar?`;
    confirmModal.style.display = "flex";
  });

  // Cancelar modal
  cancelSend.addEventListener("click", () => {
    confirmModal.style.display = "none";
  });

  // Confirmar envío
  confirmSend.addEventListener("click", () => {
    confirmModal.style.display = "none";

    const courseName = courses.find(c => c.id === selectedCourseId)?.name || selectedCourseId;
    const text = `[${courseName}] ${selectedType}${selectedFile ? `\nArchivo: ${selectedFile.name}` : ""}`;
    const encoded = encodeURIComponent(text);
    const url = groupLinks[selectedCourseId] || `https://web.whatsapp.com/send?text=${encoded}`;
    
    // Abrir WhatsApp
    window.open(url, "_blank");

    // Crear entrada de historial
    const historyEntry = {
      archivo: selectedFile?.name || "Sin archivo",
      curso: courseName,
      tipo: selectedType,
      usuario: "Tú", // Cambia si tienes sistema de usuarios
      fecha: new Date().toLocaleString(),
      estado: "Enviado"
    };

    // Guardar en localStorage
    const history = JSON.parse(localStorage.getItem("historialWhatsApp") || "[]");
    history.push(historyEntry);
    localStorage.setItem("historialWhatsApp", JSON.stringify(history));

    // Agregar visualmente
    addHistoryRow(historyEntry);
  });

  // Evento: limpiar formulario
  clearBtn.addEventListener("click", () => location.reload());

  // Evento: limpiar historial (si existe el botón)
  const clearHistoryBtn = $("clearHistory");
  if (clearHistoryBtn) {
    clearHistoryBtn.addEventListener("click", () => {
      if (confirm("¿Estás seguro de que deseas borrar el historial?")) {
        localStorage.removeItem("historialWhatsApp");
        $("historyBody").innerHTML = "";
      }
    });
  }

  // Cargar historial al iniciar
  const savedHistory = JSON.parse(localStorage.getItem("historialWhatsApp") || "[]");
  savedHistory.forEach(addHistoryRow);

  // Activar botón solo si curso y tipo están seleccionados
  function updateControls() {
    sendBtn.disabled = !(selectedCourseId && selectedType);
  }
});

// Agrega fila a la tabla del historial
function addHistoryRow(entry) {
  const historyBody = $("historyBody");
  const tr = document.createElement("tr");
  tr.innerHTML = `
    <td>${entry.archivo}</td>
    <td>${entry.curso}</td>
    <td>${entry.tipo}</td>
    <td>${entry.usuario}</td>
    <td>${entry.fecha}</td>
    <td>${entry.estado}</td>
  `;
  historyBody.appendChild(tr);
}
