const fileInput = document.getElementById("fileInput");
const uploadArea = document.getElementById("uploadArea");
const uploadIcon = document.getElementById("uploadIcon");
const uploadText = document.getElementById("uploadText");
const preview = document.getElementById("preview");

const btnPublicar = document.getElementById("btnPublicar");

// Modal dinámico (lo creamos desde JS)
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

// 📌 Botón confirmar → enviar
confirmSend.addEventListener("click", () => {
  confirmModal.style.display = "none";

  const fecha = document.getElementById("fecha").value;
  const titulo = document.querySelector("input[placeholder='Escribe el título de la noticia']").value;
  const contenido = document.getElementById("contenido").value;
  const creadoPor = document.getElementById("titulo").value || "Anónimo";

  let imagen = "";
  if (preview.querySelector("img")) {
    imagen = preview.querySelector("img").src;
  }

  // --- Guardar noticia ---
  let noticias = JSON.parse(localStorage.getItem("noticias")) || [];

  // Si hay menos de 4 noticias → agregar en orden
  if (noticias.length < 4) {
    noticias.push({ fecha, titulo, contenido, creadoPor, imagen });
  } else {
    // Si ya hay 4 → buscar la posición para sobrescribir
    let siguienteIndex = noticias.findIndex(n => !n);
    if (siguienteIndex === -1) {
      siguienteIndex = 0; // reinicia en Noticia 1
    }
    noticias[siguienteIndex] = { fecha, titulo, contenido, creadoPor, imagen };
  }

  localStorage.setItem("noticias", JSON.stringify(noticias));

  alert("✅ Noticia publicada correctamente");
});

document.addEventListener("DOMContentLoaded", () => {
  const contenedor = document.getElementById("circular1-contenido");

  const circular = JSON.parse(localStorage.getItem("circular1"));

  if (circular) {
    if (circular.type.startsWith("image/")) {
      contenedor.innerHTML = `<img src="${circular.data}" 
                                class="img-fluid rounded shadow-sm" 
                                style="max-height:400px;">`;
    } else if (circular.type === "application/pdf") {
      contenedor.innerHTML = `<embed src="${circular.data}" 
                                type="application/pdf" 
                                width="100%" height="400px">`;
    } else {
      contenedor.innerHTML = `<p class="text-muted">Archivo: ${circular.name}</p>`;
    }
  }
});


// 🔔 Manejo de notificaciones (campanita)
document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("formNotificacionDropdown");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const datos = {
      correo: document.getElementById("correoNoti").value.trim(),
      titulo: document.getElementById("tituloNoti").value.trim(),
      mensaje: document.getElementById("mensajeNoti").value.trim()
    };

    if (!datos.correo || !datos.titulo || !datos.mensaje) {
      Swal.fire("Campos incompletos", "Por favor llena todos los campos.", "warning");
      return;
    }

    try {
      const res = await fetch("/enviar_notificacion", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(datos)
      });

      const result = await res.json();

      if (result.status === "ok") {
        Swal.fire("✅ Enviado", "La notificación se envió correctamente.", "success");

        // Agregar notificación a la lista de recientes
        const lista = document.getElementById("notificacionesRecientes");
        const nueva = document.createElement("div");
        nueva.classList.add("border-bottom", "pb-1", "mb-1");
        nueva.innerHTML = `
          <strong>${datos.titulo}</strong><br>
          <small>${datos.mensaje}</small><br>
          <span class="text-muted small">${datos.correo}</span>
        `;
        lista.prepend(nueva);

        // Limpiar formulario
        form.reset();
      } else {
        throw new Error(result.msg || "Error desconocido");
      }
    } catch (error) {
      Swal.fire("❌ Error", "No se pudo enviar la notificación.", "error");
      console.error(error);
    }
  });
});

const contador = document.getElementById("contadorMensajes");
  const listaMensajes = document.getElementById("listaMensajes");
  const sonido = document.getElementById("notificacionSonido");

  async function cargarNotificaciones() {
    try {
      const response = await fetch("/notificaciones");
      const data = await response.json();
      mostrarNotificaciones(data);
    } catch (error) {
      console.error("Error cargando notificaciones:", error);
    }
  }

  function mostrarNotificaciones(data) {
    listaMensajes.innerHTML = "";
    if (data.length === 0) {
      listaMensajes.innerHTML = "<p class='text-center text-muted mb-0'>No tienes mensajes nuevos.</p>";
      contador.style.display = "none";
      return;
    }

    contador.style.display = "inline-block";
    contador.textContent = data.length;

    data.forEach(n => {
      const item = document.createElement("li");
      item.classList.add("dropdown-item", "border-bottom", "small");
      item.innerHTML = `<strong>${n.titulo}</strong><br>${n.contenido}<br><small class="text-muted">${n.fecha}</small>`;
      listaMensajes.appendChild(item);
    });
  }

  // Refresca cada cierto tiempo (por ejemplo, cada 15 segundos)
  setInterval(cargarNotificaciones, 15000);

  // Carga inicial
  cargarNotificaciones();