document.addEventListener("DOMContentLoaded", async () => {
  console.log("✅ Script NoticiasVistas cargado correctamente.");

  const contenedor = document.getElementById("noticiasContainer");

  if (!contenedor) {
    console.error("❌ No se encontró el contenedor de noticias (#noticiasContainer)");
    return;
  }

  contenedor.innerHTML = "<p>Cargando noticias...</p>";

  try {
    // Se agrega timestamp para evitar caché
    const res = await fetch(`/administrador/noticias/historial?ts=${Date.now()}`, {
      cache: "no-store",
    });

    if (!res.ok) {
      throw new Error(`Error HTTP ${res.status}`);
    }

    const data = await res.json();
    console.log("📡 Respuesta del servidor:", data);

    if (data.success && Array.isArray(data.noticias) && data.noticias.length > 0) {
      contenedor.innerHTML = ""; // limpiar el "Cargando..."

      data.noticias.slice(0, 4).forEach((noticia, index) => {
        console.log(`📰 Renderizando noticia ${index + 1}:`, noticia);

        const card = document.createElement("div");
        card.className = "col-md-6 col-lg-3 d-flex";

        const imagen = noticia.archivo_url && noticia.archivo_url.trim() !== ""
          ? noticia.archivo_url
          : "/static/img/default.jpg";

        const titulo = noticia.titulo || "Sin título";
        const redaccion = noticia.redaccion || "Sin contenido.";
        const autor = noticia.creado_por || "Sistema";
        const fecha = noticia.fecha || "Fecha no disponible";

        card.innerHTML = `
          <div class="card shadow-sm flex-fill h-100 border-0">
            <img src="${imagen}" class="card-img-top" alt="Imagen de la noticia" style="object-fit: cover; height: 180px;">
            <div class="card-body d-flex flex-column">
              <h5 class="card-title text-truncate">${titulo}</h5>
              <p class="card-text small text-secondary text-truncate" style="max-height: 60px;">${redaccion}</p>
              <div class="mt-auto">
                <small class="text-muted d-block">Por: ${autor}</small>
                <small class="text-muted">📅 ${fecha}</small>
              </div>
            </div>
          </div>
        `;

        contenedor.appendChild(card);
      });
    } else {
      console.warn("⚠️ No hay noticias disponibles o error en formato.");
      contenedor.innerHTML = `<p class="text-warning text-center">No hay noticias disponibles.</p>`;
    }

  } catch (err) {
    console.error("💥 Error al cargar noticias:", err);
    contenedor.innerHTML = `
      <p class="text-danger text-center mt-3">
        Error al conectar con el servidor.<br>
        <small>${err.message}</small>
      </p>`;
  }
});
