document.addEventListener('DOMContentLoaded', () => {
  const selCurso = document.getElementById('selCurso');
  const selPeriodo = document.getElementById('selPeriodo');
  const inputBusqueda = document.getElementById('busqueda');
  const tbody = document.querySelector('#tablaPromedios tbody');

  const fetchJson = async (url) => {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  };

  const cargarCursos = async () => {
    try {
      const data = await fetchJson('/administrador/cursos/lista');
      if (data.success) {
        const opts = data.cursos.map(c => {
          const nombre = c.nombre || `${c.grado || ''}${c.grupo || ''}`;
          return `<option value="${c.id}">${nombre}</option>`;
        }).join('');
        selCurso.insertAdjacentHTML('beforeend', opts);
      }
    } catch (e) {
      console.error('Error cargando cursos', e);
    }
  };

  const getNivelColor = (prom) => {
    if (prom == null || isNaN(prom)) return {label: 'Sin datos', color: '#6c757d'}; // gris
    if (prom < 2) return {label: 'Bajo', color: '#dc3545'}; // rojo
    if (prom >= 4 && prom <= 5) return {label: 'Alto', color: '#28a745'}; // verde
    if (prom >= 3 && prom < 4) return {label: 'Medio', color: '#ffc107'}; // amarillo
    // para 2.0 - 2.99
    return {label: 'Básico', color: '#17a2b8'}; // celeste
  };

  const render = (items) => {
    const q = (inputBusqueda.value || '').toLowerCase();
    const fil = items.filter(it =>
      (it.nombre || '').toLowerCase().includes(q) ||
      (String(it.documento || '')).includes(q)
    );

    if (fil.length === 0) {
      tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">Sin datos para los filtros seleccionados.</td></tr>';
      return;
    }

    tbody.innerHTML = fil.map(it => {
      const nivel = getNivelColor(it.promedio);
      const dot = `<span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:${nivel.color};"></span>`;
      return `
        <tr>
          <td>${it.curso}</td>
          <td>${it.nombre}</td>
          <td>${it.documento || ''}</td>
          <td class="text-center">${(it.promedio ?? 0).toFixed(2)}</td>
          <td class="text-center">${dot} <small class="text-muted">${nivel.label}</small></td>
        </tr>`;
    }).join('');
  };

  const cargarPromedios = async () => {
    try {
      const curso = selCurso.value || 'all';
      const periodo = selPeriodo.value || '1';
      const url = `/administrador/promedios?curso_id=${encodeURIComponent(curso)}&periodo=${encodeURIComponent(periodo)}`;
      const data = await fetchJson(url);
      if (data.success) {
        render(data.items || []);
      } else {
        tbody.innerHTML = `<tr><td colspan="5" class="text-center text-danger">${data.error || 'Error'}</td></tr>`;
      }
    } catch (e) {
      console.error('Error cargando promedios', e);
      tbody.innerHTML = '<tr><td colspan="5" class="text-center text-danger">No se pudieron cargar los promedios.</td></tr>';
    }
  };

  // Eventos
  selCurso.addEventListener('change', cargarPromedios);
  selPeriodo.addEventListener('change', cargarPromedios);
  inputBusqueda.addEventListener('input', () => {
    // re-render con el cache actual si existe
    cargarPromedios();
  });

  // Init
  (async () => {
    await cargarCursos();
    await cargarPromedios();
  })();
});
