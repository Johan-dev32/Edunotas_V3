// Función para obtener parámetros de la URL
function obtenerParametro(nombre) {
  const urlParams = new URLSearchParams(window.location.search);
  return urlParams.get(nombre);
}

// Cambiar el título según la materia
document.addEventListener('DOMContentLoaded', () => {
  const materia = obtenerParametro('materia');
  if (materia) {
    const title = document.querySelector('.titulo-principal');
    const desc = document.querySelector('.descripcion');
    if (title) title.textContent = materia.toUpperCase();
    if (desc) desc.textContent = `Notas de la materia ${materia}`;
  }
});

document.addEventListener('DOMContentLoaded', () => {
  const periodoSelect = document.getElementById('periodoSelect');
  const tabla = document.getElementById('tablaNotasResumen');
  const tbody = tabla ? tabla.querySelector('tbody') : null;
  const promedioGeneralSpan = document.getElementById('promedioGeneralValor');
  const estudianteId = obtenerParametro('estudiante_id');
  const asignaturaId = obtenerParametro('asignatura_id');

  if (!tabla || !tbody || !periodoSelect || !promedioGeneralSpan) return;

  function fmt(v) {
    if (v === null || v === undefined || v === '') return '-';
    const n = Number(v);
    if (Number.isNaN(n)) return '-';
    return n.toFixed(2);
  }

  async function cargar(periodo) {
    tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted">Cargando notas...</td></tr>';
    promedioGeneralSpan.textContent = '-';
    try {
      const params = new URLSearchParams();
      params.set('ts', Date.now());
      if (periodo) params.set('periodo', periodo);
      if (estudianteId) params.set('estudiante_id', estudianteId);
      if (asignaturaId) params.set('asignatura', asignaturaId);
      const res = await fetch(`/estudiante/api/notas?${params.toString()}`, { cache: 'no-store' });
      if (!res.ok) throw new Error('HTTP ' + res.status);
      const data = await res.json();
      if (!data.success) throw new Error('Respuesta inválida');

      const notas = Array.isArray(data.notas) ? data.notas : [];
      if (notas.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted">No hay notas registradas para este período.</td></tr>';
        return;
      }

      // Si no se especificó período, poblar el select con los períodos reales y elegir el más reciente disponible
      if (!periodo) {
        const periodos = [...new Set(notas.map(n => n.periodo))].sort((a,b)=>b-a);
        // Rellenar el select dinámicamente
        periodoSelect.innerHTML = '';
        periodos.slice().sort((a,b)=>a-b).forEach(p => {
          const opt = document.createElement('option');
          opt.value = String(p);
          opt.textContent = String(p);
          periodoSelect.appendChild(opt);
        });
        const elegido = periodos[0];
        periodoSelect.value = String(elegido);
        // volver a cargar ya filtrado
        return cargar(elegido);
      }

      // Agrupar por asignatura_id (aunque generalmente ya es 1 fila por asignatura+periodo)
      const porAsig = new Map();
      notas.forEach(r => {
        const key = r.asignatura_id;
        if (!porAsig.has(key)) porAsig.set(key, r);
        else {
          // Si existiera más de un registro por asignatura, priorizamos promedio más reciente o combinamos
          porAsig.set(key, r);
        }
      });

      // Render (con filtro opcional por materia via querystring)
      tbody.innerHTML = '';
      let sumaPromedios = 0;
      let cuentaPromedios = 0;
      const filtroMateria = asignaturaId ? '' : (obtenerParametro('materia') || '').toLowerCase().trim();
      console.log(`[DEBUG] Filtro materia: "${filtroMateria}"`);
      const filas = [];
      porAsig.forEach(r => {
        if (asignaturaId && String(r.asignatura_id) !== String(asignaturaId)) {
          console.log(`[DEBUG] Descartado por ID: ${r.asignatura_id} != ${asignaturaId}`);
          return;
        }
        if (filtroMateria && !(r.asignatura || '').toLowerCase().includes(filtroMateria)) {
          console.log(`[DEBUG] Descartado por nombre: "${r.asignatura}" no incluye "${filtroMateria}"`);
          return;
        }
        console.log(`[DEBUG] Aceptado: ${r.asignatura} (ID: ${r.asignatura_id})`);
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td>${r.asignatura || 'Asignatura'}</td>
          <td class="text-center">${fmt(r.nota_1)}</td>
          <td class="text-center">${fmt(r.nota_2)}</td>
          <td class="text-center">${fmt(r.nota_3)}</td>
          <td class="text-center">${fmt(r.nota_4)}</td>
          <td class="text-center">${fmt(r.nota_5)}</td>
          <td class="text-center fw-bold">${fmt(r.promedio)}</td>
        `;
        filas.push(tr);
        if (r.promedio !== null && r.promedio !== undefined) {
          const n = Number(r.promedio);
          if (!Number.isNaN(n)) { sumaPromedios += n; cuentaPromedios += 1; }
        }
      });

      if (filas.length === 0) {
        if (filtroMateria) {
          console.warn('No se encontraron notas para la materia filtrada. Mostrando todas.');
          // Renderizar todas sin filtro
          porAsig.forEach(r => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
              <td>${r.asignatura || 'Asignatura'}</td>
              <td class="text-center">${fmt(r.nota_1)}</td>
              <td class="text-center">${fmt(r.nota_2)}</td>
              <td class="text-center">${fmt(r.nota_3)}</td>
              <td class="text-center">${fmt(r.nota_4)}</td>
              <td class="text-center">${fmt(r.nota_5)}</td>
              <td class="text-center fw-bold">${fmt(r.promedio)}</td>
            `;
            tbody.appendChild(tr);
          });
        } else {
          tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted">No hay notas para la asignatura seleccionada en este período.</td></tr>';
        }
      } else {
        filas.forEach(tr => tbody.appendChild(tr));
      }

      // Si no hay 'materia' en la URL, intenta titular con el nombre de la primera asignatura cuando hay filtro por asignatura_id
      if (!obtenerParametro('materia') && asignaturaId && filas.length > 0) {
        const primera = porAsig.get(Number(asignaturaId));
        const title = document.querySelector('.titulo-principal');
        const desc = document.querySelector('.descripcion');
        if (primera && primera.asignatura) {
          if (title) title.textContent = primera.asignatura.toUpperCase();
          if (desc) desc.textContent = `Notas de la materia ${primera.asignatura}`;
        }
      }

      console.log(`[DEBUG] Filas totales: ${filas.length}`);
      console.log(`[DEBUG] porAsig size: ${porAsig.size}`);
      
      // Si es una sola materia, mostrar su promedio como promedio general
      if (filas.length === 1) {
        const primeraFila = filas[0];
        const promedioCelda = primeraFila.cells[6]; // Celda del promedio
        console.log(`[DEBUG] Fila encontrada: ${primeraFila.innerHTML}`);
        console.log(`[DEBUG] Celda promedio: ${promedioCelda ? promedioCelda.textContent : 'No encontrada'}`);
        
        if (promedioCelda) {
          const promedioTexto = promedioCelda.textContent.trim();
          if (promedioTexto !== '-') {
            promedioGeneralSpan.textContent = promedioTexto;
            console.log(`[DEBUG] Promedio asignado: ${promedioTexto}`);
          }
        }
      } else {
        promedioGeneralSpan.textContent = cuentaPromedios > 0 ? (sumaPromedios / cuentaPromedios).toFixed(2) : '-';
      }
      console.log(`[DEBUG] Promedio general - Suma: ${sumaPromedios}, Cuenta: ${cuentaPromedios}, Resultado: ${cuentaPromedios > 0 ? (sumaPromedios / cuentaPromedios).toFixed(2) : '-'}`);
    } catch (e) {
      console.error('Error cargando notas:', e);
      tbody.innerHTML = '<tr><td colspan="7" class="text-center text-danger">Error al cargar las notas.</td></tr>';
    }
  }

  // Carga inicial: detectar automáticamente el último período con datos
  cargar(null);
  periodoSelect.addEventListener('change', () => cargar(periodoSelect.value));
});
