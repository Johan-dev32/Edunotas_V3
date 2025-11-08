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
      elemento.classList.add("border", "rounded", "p-2", "mb-1", "bg-light", "small");
      elemento.innerHTML = `<strong>${noti.titulo}</strong><br>${noti.contenido}`;
      contenedor.appendChild(elemento);
    });
  } catch (error) {
    console.error("Error al obtener notificaciones:", error);
  }
}

document.getElementById("btnEnviarNotificacion")?.addEventListener("click", enviarNotificacion);
setInterval(obtenerNotificaciones, 15000);
document.addEventListener("DOMContentLoaded", obtenerNotificaciones);