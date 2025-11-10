const fileInput = document.getElementById("fileInput");
const uploadArea = document.getElementById("uploadArea");
const uploadIcon = document.getElementById("uploadIcon");
const uploadText = document.getElementById("uploadText");
const preview = document.getElementById("preview");

const btnPublicar = document.getElementById("btnPublicar");

// Modal dinámico
const confirmModal = document.createElement("div");
confirmModal.className = "custom-modal";
confirmModal.style.cssText = `
  display: none;
  position: fixed; 
  top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0,0,0,0.6); 
  justify-content: center; 
  align-items: center;
  z-index: 1050;
`;
confirmModal.innerHTML = `
  <div class="bg-white rounded shadow p-4" style="max-width: 400px; width: 90%;">
    <div class="d-flex align-items-center mb-3">
      <i class="bi bi-exclamation-triangle-fill text-warning fs-4 me-2"></i>
      <h5 class="m-0 fw-bold">Confirmar envío</h5>
    </div>
    <p id="confirmText" class="mb-2"></p>
    <p class="mb-0">¿Deseas continuar?</p>
    <div class="d-flex justify-content-end gap-2 mt-3">
      <button id="cancelSend" class="btn btn-secondary">Cancelar</button>
      <button id="confirmSend" class="btn btn-danger">Subir</button>
    </div>
  </div>
`;
document.body.appendChild(confirmModal);

const confirmText = confirmModal.querySelector("#confirmText");
const cancelSend = confirmModal.querySelector("#cancelSend");
const confirmSend = confirmModal.querySelector("#confirmSend");

// 📌 Abrir input al hacer click en el área
uploadArea.addEventListener("click", () => fileInput.click());

// 📌 Mostrar preview al seleccionar archivo
fileInput.addEventListener("change", () => {
  preview.innerHTML = ""; // limpiar preview anterior

  if (fileInput.files.length > 0) {
    const file = fileInput.files[0];

    if (file.type.startsWith("image/")) {
      const reader = new FileReader();
      reader.onload = e => {
        // ocultar ícono y texto
        uploadIcon.style.display = "none";
        uploadText.style.display = "none";

        // mostrar imagen
        const img = document.createElement("img");
        img.src = e.target.result;
        img.classList.add("img-fluid", "rounded");
        img.style.maxHeight = "250px";
        preview.appendChild(img);
      };
      reader.readAsDataURL(file);
    } else {
      preview.innerHTML = `<p class="text-danger">⚠️ Solo se permiten imágenes.</p>`;
    }
  }
});

// 📌 Abrir modal al dar click en "Publicar Noticia"
btnPublicar.addEventListener("click", (e) => {
  e.preventDefault(); // evita que se envíe el form directo

  const fecha = document.getElementById("fecha").value;
  const titulo = document.getElementById("titulo").value;
  const contenido = document.getElementById("contenido").value;

  confirmText.textContent = ` Fecha: ${fecha || "No seleccionada"} |  Título: ${titulo || "Sin título"} |  Contenido: ${contenido.substring(0, 30)}...`;

  confirmModal.style.display = "flex"; // mostrar modal
});

// 📌 Botón cancelar → cerrar modal
cancelSend.addEventListener("click", () => {
  confirmModal.style.display = "none";
});

// 📌 Botón confirmar → enviar noticia
// En Noticias.js, reemplazar la sección 'Botón confirmar → enviar noticia'

confirmSend.addEventListener("click", async () => {
  confirmModal.style.display = "none";

  const formNoticias = document.getElementById("formNoticias");
  const fileInput = document.getElementById("fileInput"); // Asegúrate de que fileInput esté disponible

  // Crear FormData para enviar texto y archivo
  const formData = new FormData();
  
  formData.append("fecha", document.getElementById("fecha").value);
  formData.append("titulo", document.getElementById("titulo").value);
  formData.append("contenido", document.getElementById("contenido").value);
  // Usamos "creadoPor" como un campo de texto simple
  formData.append("creadoPor", document.getElementById("creadoPor").value || "Anónimo");

  // Añadir el archivo. Usa 'archivo' como nombre de campo (debe coincidir con Flask)
  if (fileInput.files.length > 0) {
    formData.append("archivo", fileInput.files[0]);
  }
 try {
        const res = await fetch("/administrador/noticias/registro", {
            method: "POST",
            body: formData,
        });

        // Manejo de errores HTTP (400, 500, etc.)
        if (!res.ok) {
            // Intenta leer el error detallado del JSON si Flask lo proporciona
            const errorData = await res.json().catch(() => ({ error: "Error de servidor no especificado." }));
            alert("❌ Error al publicar noticia: " + (errorData.error || `Error HTTP ${res.status}.`));
            return;
        }
        
        const data = await res.json();

        if (data.success) {
            alert("✅ Noticia publicada correctamente en la Base de Datos.");
            // Limpiar formulario y redireccionar
            formNoticias.reset();
            window.location.href = "Administrador/noticias_vistas";// O la ruta que desees
        } else {
            // Manejo de errores de validación de Flask (success: false)
            alert("❌ Error al publicar noticia: " + (data.error || "Fallo desconocido."));
        }

    } catch (error) {
        console.error("Error de conexión (red o CORS):", error);
        // ✨ CORRECCIÓN: Usamos un mensaje más simple para errores de red/fetch
        alert("🛑 La conexión falló. Por favor, revisa tu red o intenta más tarde.");
    }
});