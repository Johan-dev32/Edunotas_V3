const fileInput = document.getElementById("fileInput");
const uploadArea = document.getElementById("uploadArea");
const uploadIcon = document.getElementById("uploadIcon");
const uploadText = document.getElementById("uploadText");
const preview = document.getElementById("preview");

const btnPublicar = document.getElementById("btnPublicar");
const formNoticias = document.querySelector("form"); // Busca el único formulario en la página (Asegúrate de darle un ID como "formNoticias" en HTML, ver paso 2.A)


// Modal dinámico
const confirmModal = document.createElement("div");
// ... (código del modal) ...
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
  
  if (!fecha || !titulo || !contenido) {
    alert("⚠️ Por favor, rellene todos los campos obligatorios (Fecha, Título, Redacción).");
    return;
  }

  confirmText.textContent = ` Fecha: ${fecha} |  Título: ${titulo} |  Contenido: ${contenido.substring(0, 30)}...`;

  confirmModal.style.display = "flex"; // mostrar modal
});

// 📌 Botón cancelar → cerrar modal
cancelSend.addEventListener("click", () => {
  confirmModal.style.display = "none";
});

// 📌 Botón confirmar → enviar noticia

confirmSend.addEventListener("click", async () => {
  confirmModal.style.display = "none";
  
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
            // Limpiar formulario y redireccionar (asumiendo que formNoticias es el formulario)
            formNoticias.reset(); // Usa el formulario que obtuviste al inicio

            // ⚠️ CLAVE: Redirige usando una URL absoluta
            window.location.href = "/administrador/noticias"; // Ajusta esta URL a tu vista de noticias (puedes usar la ruta de la función 'noticias' si esa es la vista principal)
        } else {
            // Manejo de errores de validación de Flask (success: false)
            alert("❌ Error al publicar noticia: " + (data.error || "Fallo desconocido."));
        }

    } catch (error) {
        console.error("Error de conexión (red o CORS):", error);
        // Este mensaje solo sale si falla la conexión de red (el navegador no pudo contactar al servidor)
        alert("🛑 La conexión falló. Por favor, revisa tu red o intenta más tarde.");
    }
});