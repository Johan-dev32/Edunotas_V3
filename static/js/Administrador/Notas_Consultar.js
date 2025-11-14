document.addEventListener('DOMContentLoaded', () => {
  const selCurso = document.getElementById('selectCurso');
  const selAsig = document.getElementById('selectAsignatura');
  const selPeriodo = document.getElementById('selectPeriodo');
  const tbody = document.getElementById('tbodyNotas');

  const fetchJson = async (url) => {
    const res = await fetch(url + (url.includes('?') ? '&' : '?') + 'ts=' + Date.now(), { cache: 'no-store' });
    if (!res.ok) throw new Error('HTTP ' + res.status);
    return res.json();
  };

  const cargarCursos = async () => {
    try {
      const data = await fetchJson('/administrador/cursos/lista');
      if (data.success && Array.isArray(data.cursos)) {
        selCurso.innerHTML = '<option value="">Seleccione...</option>' +
          data.cursos.map(c => `<option value="${c.id}">${c.nombre || (c.grado + '-' + c.grupo)}</option>`).join('');
      }
    } catch (e) {
      console.error('Error cargando cursos', e);
    }
  };

  const cargarAsignaturas = async () => {
    try {
      const cursoId = (window.CURSO_ID || selCurso.value || '').toString();
      const url = cursoId ? `/administrador/asignaturas/lista?curso_id=${encodeURIComponent(cursoId)}` : '/administrador/asignaturas/lista';
      const data = await fetchJson(url);
      if (data.success && Array.isArray(data.asignaturas)) {
        selAsig.innerHTML = '<option value="">Seleccione...</option>' +
          data.asignaturas.map(a => `<option value="${a.id}">${a.nombre}</option>`).join('');
        // Autoselect y carga automática
        const hasValue = selAsig.value && selAsig.value !== '';
        if (!hasValue && data.asignaturas.length > 0) {
          selAsig.value = String(data.asignaturas[0].id);
          // Si ya hay curso y período definidos, cargar notas automáticamente
          if ((window.CURSO_ID || selCurso.value) && selPeriodo.value) {
            cargarNotas();
          }
        }
      }
    } catch (e) {
      console.error('Error cargando asignaturas', e);
    }
  };

  const renderNotas = (items) => {
    if (!items || items.length === 0) {
      tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted">Sin datos para los filtros seleccionados.</td></tr>';
      return;
    }
    tbody.innerHTML = items.map(it => {
      const nombre = `${it.apellido || ''} ${it.nombre || ''}`.trim();
      const fmt = (v) => (v === null || v === undefined) ? '' : v;
      return `
        <tr>
          <td>${nombre}</td>
          <td>${fmt(it.nota_1)}</td>
          <td>${fmt(it.nota_2)}</td>
          <td>${fmt(it.nota_3)}</td>
          <td>${fmt(it.nota_4)}</td>
          <td>${fmt(it.nota_5)}</td>
          <td><strong>${fmt(it.promedio_final)}</strong></td>
        </tr>`;
    }).join('');
  };

  const cargarNotas = async () => {
    const cursoId = selCurso.value;
    const asigId = selAsig.value;
    const periodo = selPeriodo.value;
    if (!cursoId || !asigId || !periodo) {
      tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted">Seleccione curso, asignatura y período para ver las notas.</td></tr>';
      return;
    }
    tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted">Cargando...</td></tr>';
    try {
      const q = `/administrador/notas?curso_id=${encodeURIComponent(cursoId)}&asignatura_id=${encodeURIComponent(asigId)}&periodo=${encodeURIComponent(periodo)}`;
      const data = await fetchJson(q);
      if (data.success) {
        renderNotas(data.notas);
      } else {
        tbody.innerHTML = `<tr><td colspan="7" class="text-center text-danger">${data.error || 'Error al cargar notas.'}</td></tr>`;
      }
    } catch (e) {
      console.error('Error cargando notas', e);
      tbody.innerHTML = '<tr><td colspan="7" class="text-center text-danger">Error de conexión al cargar notas.</td></tr>';
    }
  };

  // Eventos
  selCurso.addEventListener('change', async () => {
    await cargarAsignaturas();
    await cargarNotas();
  });
  selAsig.addEventListener('change', cargarNotas);
  selPeriodo.addEventListener('change', cargarNotas);

  // Init
  if (window.CURSO_ID) {
    // Preseleccionar curso y evitar recarga de lista completa
    if (selCurso) {
      selCurso.value = String(window.CURSO_ID);
    }
    cargarAsignaturas();
  } else {
    cargarCursos().then(cargarAsignaturas);
  }
});
