async function enviarNotificacion() {
  const destino = document.getElementById("destino")?.value;
  const titulo = document.getElementById("asunto")?.value.trim();
  const mensaje = document.getElementById("mensaje")?.value.trim();
  if (!destino || !titulo || !mensaje) return;

  let url = "/notificaciones/enviar_todos";
  let body = { titulo: titulo, contenido: mensaje };

  if (destino !== "Todos los roles") body.rol = destino;
  else body.rol = "Todos";

  try {
    const respuesta = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body)
    });
    if (respuesta.ok) {
      Swal.fire({
        icon: "success",
        title: "Notificación enviada",
        text: body.rol === "Todos" ? "Notificación enviada a todos los roles" : `Notificación enviada a ${body.rol}`,
        confirmButtonColor: "#5A4AE3"
      });
      document.getElementById("formNotificacion")?.reset();
      obtenerNotificaciones();
    } else {
      const error = await respuesta.json();
      Swal.fire({
        icon: "error",
        title: "Error",
        text: error.error || "No se pudo enviar la notificación",
        confirmButtonColor: "#5A4AE3"
      });
    }
  } catch (err) {
    Swal.fire({
      icon: "error",
      title: "Error de conexión",
      text: "No se pudo comunicar con el servidor.",
      confirmButtonColor: "#5A4AE3"
    });
  }
}

async function obtenerNotificaciones() {
  try {
    const respuesta = await fetch("/notificaciones/recibir");
    if (!respuesta.ok) return;

    const notificaciones = await respuesta.json();
    const contenedor = document.getElementById("notificacionesRecientes");
    if (!contenedor) return;

    contenedor.innerHTML = "";
    if (notificaciones.length === 0) {
      contenedor.innerHTML = `<p class="text-center small text-secondary">Sin notificaciones recientes</p>`;
      return;
    }

    notificaciones.forEach(noti => {
      const elemento = document.createElement("div");
      elemento.className = "list-group-item border-0 p-2 mb-1";
      const titulo = document.createElement("div");
      titulo.className = "fw-semibold text-dark small";
      titulo.textContent = noti.titulo;
      const cuerpo = document.createElement("div");
      cuerpo.className = "text-muted small mt-1";
      cuerpo.style.whiteSpace = 'pre-wrap';
      cuerpo.style.wordBreak = 'break-word';
      cuerpo.textContent = noti.contenido;
      elemento.appendChild(titulo);
      elemento.appendChild(cuerpo);
      contenedor.appendChild(elemento);
    });
  } catch (error) {
    console.error("Error al obtener notificaciones:", error);
  }
}

// --- Contador de no leídas (badge/punto rojo) ---
async function actualizarContadorNotificaciones() {
  try {
    const res = await fetch('/notificaciones/contador');
    if (!res.ok) return;
    const data = await res.json();
    const badge = document.getElementById('contadorMensajes');
    if (!badge) return;
    const n = Number(data.unread || 0);
    if (n > 0) {
      badge.style.display = 'inline-block';
      badge.textContent = n;
    } else {
      badge.style.display = 'none';
      badge.textContent = '0';
    }
  } catch (e) {
    // Silencioso
  }
}

// Marcar como leídas al abrir el dropdown de la campana
function wireDropdownMarkAsRead() {
  const trigger = document.getElementById('dropdownMenuButton');
  if (!trigger) return;
  trigger.addEventListener('show.bs.dropdown', async () => {
    try {
      await fetch('/notificaciones/marcar_leidas', { method: 'POST' });
      // Refrescar listado y contador
      obtenerNotificaciones();
      actualizarContadorNotificaciones();
    } catch (e) {}
  });
}

document.getElementById("btnEnviarNotificacion")?.addEventListener("click", enviarNotificacion);

// Polling
setInterval(() => { obtenerNotificaciones(); actualizarContadorNotificaciones(); }, 15000);

document.addEventListener("DOMContentLoaded", () => {
  obtenerNotificaciones();
  actualizarContadorNotificaciones();
  wireDropdownMarkAsRead();
});