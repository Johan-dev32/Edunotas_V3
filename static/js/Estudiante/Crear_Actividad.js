// Carga dinámica de tutorías del estudiante sin cambiar el HTML
// Reemplaza el contenido de .grid-tutorias con las tarjetas generadas

document.addEventListener('DOMContentLoaded', async () => {
  const grid = document.querySelector('.grid-tutorias');
  if (!grid) return;

  const fmtFecha = (iso) => {
    if (!iso) return '';
    try { const [y,m,d] = iso.split('-').map(Number); return `${String(d).padStart(2,'0')}/${String(m).padStart(2,'0')}/${y}`; } catch { return iso; }
  };

  const crearTarjeta = (t, idx) => {
    const cont = document.createElement('div');
    cont.className = 'detalle-contenedor';
    cont.innerHTML = `
      <h2 class="titulo-principal2">Tutoría ${idx + 1}</h2>
      <p class="descripcion">Información registrada por el administrador o docente.</p>
      <div class="info-general">
        <p><strong>Nombre:</strong> ${t.nombre || ''}</p>
        <p><strong>Rol:</strong> ${t.rol || ''}</p>
        <p><strong>Tema:</strong> ${t.tema || ''}</p>
        <p><strong>Fecha:</strong> ${fmtFecha(t.fecha)}</p>
        <p><strong>Curso:</strong> ${t.curso || ''}</p>
        <p><strong>Motivo:</strong> ${t.motivo || ''}</p>
      </div>
      <div class="mensaje-docente">
        <strong>Observaciones:</strong>
        <p>${t.observaciones || ''}</p>
      </div>
    `;
    return cont;
  };

  grid.innerHTML = '<div class="text-muted">Cargando tutorías...</div>';
  try {
    const res = await fetch('/estudiante/tutorias/historial?ts=' + Date.now(), { cache: 'no-store' });
    if (!res.ok) throw new Error('HTTP ' + res.status);
    const data = await res.json();

    if (!data.success) {
      grid.innerHTML = '<div class="text-danger">No fue posible cargar tus tutorías.</div>';
      return;
    }
    const lista = Array.isArray(data.tutorias) ? data.tutorias : [];
    if (lista.length === 0) {
      grid.innerHTML = '<div class="text-muted">Aún no tienes tutorías registradas.</div>';
      return;
    }

    const MAX_CARDS = 3;
    grid.innerHTML = '';
    lista.slice(0, MAX_CARDS).forEach((t, i) => grid.appendChild(crearTarjeta(t, i)));
  } catch (e) {
    console.error('Error cargando tutorías:', e);
    grid.innerHTML = '<div class="text-danger">Error al cargar tutorías.</div>';
  }
});

// ------------------- CITACIONES (Estudiante) -------------------
document.addEventListener('DOMContentLoaded', async () => {
  const cards = Array.from(document.querySelectorAll('.card.card-citacion'));
  if (cards.length === 0) return;

  const fmtFecha = (iso) => {
    if (!iso) return '';
    try { const [y,m,d] = iso.split('-').map(Number); return `${String(d).padStart(2,'0')}/${String(m).padStart(2,'0')}/${y}`; } catch { return iso; }
  };

  try {
    const res = await fetch('/estudiante/citaciones/historial?ts=' + Date.now(), { cache: 'no-store' });
    if (!res.ok) throw new Error('HTTP ' + res.status);
    const data = await res.json();
    if (!data.success) throw new Error('Respuesta inválida');

    const lista = Array.isArray(data.citaciones) ? data.citaciones : [];
    const top = lista.slice(0, 3);

    const bodyTpl = (c) => `
      <p><strong>Fecha:</strong> ${fmtFecha(c.fecha)}</p>
      <p><strong>Correo:</strong> ${c.correo || ''}</p>
      <p><strong>Asunto:</strong> ${c.asunto || ''}</p>
      <p><strong>Citación:</strong> ${c.mensaje || ''}</p>
      <button class="btn btn-ver mt-2 w-100"><a href="/estudiante/citaciones2" class="nav-link text-white">Ver Detalles</a></button>
    `;

    cards.forEach((card, idx) => {
      const header = card.querySelector('.card-header');
      const body = card.querySelector('.card-body');
      const c = top[idx];
      if (c) {
        if (header) header.textContent = `Asunto: ${c.asunto || ''}`;
        if (body) body.innerHTML = bodyTpl(c);
        card.classList.remove('d-none');
      } else {
        card.classList.add('d-none');
      }
    });

    if (top.length === 0 && cards[0]) {
      const header = cards[0].querySelector('.card-header');
      const body = cards[0].querySelector('.card-body');
      if (header) header.textContent = 'Sin citaciones';
      if (body) body.innerHTML = '<p class="text-muted mb-0">No tienes citaciones registradas.</p>';
      cards.slice(1).forEach(c => c.classList.add('d-none'));
    }
  } catch (e) {
    console.error('Error cargando citaciones:', e);
    if (cards[0]) {
      const header = cards[0].querySelector('.card-header');
      const body = cards[0].querySelector('.card-body');
      if (header) header.textContent = 'Error al cargar citaciones';
      if (body) body.innerHTML = '<p class="text-danger mb-0">No fue posible obtener tus citaciones. Intenta nuevamente.</p>';
      cards.slice(1).forEach(c => c.classList.add('d-none'));
    }
  }
});
