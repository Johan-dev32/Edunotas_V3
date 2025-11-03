

document.addEventListener("DOMContentLoaded", () => {
  const cursoIdEl = document.getElementById('cursoId');
  if (!cursoIdEl) {
    console.error('Falta el input hidden #cursoId en el HTML');
    return;
  }
  const cursoId = cursoIdEl.value;
  const materiasSelect = document.getElementById("materias");
  const tablaNotas = document.getElementById("tablaNotas");
  const btnAgregarColumna = document.getElementById("agregarColumnaBtn");

  if (!materiasSelect || !tablaNotas) {
    console.error('Faltan elementos #materias o #tablaNotas en el HTML');
    return;
  }

  // 1) cargar materias
  async function cargarMaterias() {
    try {
      const res = await fetch(`/docente/api/materias/${cursoId}`);
      const ctype = res.headers.get('content-type') || '';
      if (ctype.includes('text/html')) {
        alert('Parece que no estás autenticado. Inicia sesión como docente e intenta de nuevo.');
        return;
      }
      const materias = await res.json();
      materiasSelect.innerHTML = `<option value="">-- Selecciona una materia --</option>`;
      materias.forEach(m => {
        const opt = document.createElement('option');
        opt.value = m.ID_Asignatura;
        opt.textContent = m.Nombre;
        materiasSelect.appendChild(opt);
      });
    } catch (err) {
      console.error(err);
      materiasSelect.innerHTML = `<option value="">(error cargando materias)</option>`;
    }
  }

  // 2) al cambiar materia -> cargar notas
  materiasSelect.addEventListener('change', () => {
    const asignaturaId = materiasSelect.value;
    if (!asignaturaId) {
      tablaNotas.querySelector('tbody')?.remove();
      tablaNotas.querySelector('thead')?.remove();
      return;
    }
    cargarNotas(asignaturaId);
  });

  // 3) cargar notas/actividades
  async function cargarNotas(asignaturaId) {
    try {
      const res = await fetch(`/docente/api/notas/${cursoId}/${asignaturaId}`);
      const ctype = res.headers.get('content-type') || '';
      if (ctype.includes('text/html')) {
        alert('Parece que no estás autenticado. Inicia sesión como docente e intenta de nuevo.');
        return;
      }
      const data = await res.json();
      const activities = data.activities || [];
      const students = data.students || [];
      const grades = data.grades || [];

      // construir encabezado
      const thead = document.createElement('thead');
      const headerRow = document.createElement('tr');
      headerRow.innerHTML = `<th>No</th><th>Estudiante</th>`;
      activities.forEach(a => headerRow.innerHTML += `<th>${a.Titulo || 'Actividad'}</th>`);
      thead.appendChild(headerRow);
      // reemplazar thead
      const oldHead = tablaNotas.querySelector('thead');
      if (oldHead) oldHead.replaceWith(thead); else tablaNotas.prepend(thead);

      // construir cuerpo
      const tbody = document.createElement('tbody');
      students.forEach((s, idx) => {
        const tr = document.createElement('tr');
        tr.innerHTML = `<td>${idx+1}</td><td>${s.Nombre}</td>`;
        activities.forEach(a => {
          const grade = grades.find(g => g.ID_Actividad === a.ID_Actividad && g.ID_Matricula === s.ID_Matricula);
          const val = grade ? (grade.Calificacion !== null ? grade.Calificacion : '') : '';
          const td = document.createElement('td');
          td.contentEditable = 'true';
          td.dataset.actividad = a.ID_Actividad;
          td.dataset.matricula = s.ID_Matricula;
          td.textContent = val;
          tr.appendChild(td);
        });
        tbody.appendChild(tr);
      });

      const oldBody = tablaNotas.querySelector('tbody');
      if (oldBody) oldBody.replaceWith(tbody); else tablaNotas.appendChild(tbody);

      if (data.warning) console.warn(data.warning);
    } catch (err) {
      console.error(err);
      alert('Error al cargar notas. Mira la consola.');
    }
  }

  // 4) crear actividad (agregar columna) - llama endpoint que crea Actividad y Cronograma
  if (btnAgregarColumna) {
    btnAgregarColumna.addEventListener('click', async () => {
      const asignaturaId = materiasSelect.value;
      if (!asignaturaId) return alert('Selecciona una materia primero.');
      const titulo = prompt('Nombre de la nueva actividad:');
      if (!titulo) return;
      try {
        const res = await fetch('/docente/api/crear_actividad', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ titulo, tipo: 'Taller', curso_id: cursoId })
        });
        const json = await res.json();
        if (json.ID_Actividad) {
          alert('Actividad creada.');
          cargarNotas(asignaturaId);
        } else {
          console.error(json);
          alert('Error al crear actividad (ver consola).');
        }
      } catch (err) {
        console.error(err);
        alert('Error al crear actividad (ver consola).');
      }
    });
  }

  // arranque
  cargarMaterias();
});

// función global para guardar (puede invocarse con onclick en HTML)
async function guardarNotas() {
  const tabla = document.getElementById('tablaNotas');
  if (!tabla) return alert('Tabla de notas no encontrada');

  const celdas = Array.from(tabla.querySelectorAll('td[contenteditable="true"], td[contenteditable]'));
  const updates = [];
  celdas.forEach(td => {
    const actividad_id = td.dataset.actividad;
    const matricula_id = td.dataset.matricula;
    const val = td.textContent.trim();
    if (!actividad_id || !matricula_id) return;
    if (val === '') return; // no enviar vacíos
    updates.push({ actividad_id, matricula_id, calificacion: val });
  });

  if (updates.length === 0) {
    return alert('No hay notas para guardar (rellena al menos un campo).');
  }

  try {
    const res = await fetch('/docente/api/guardar_notas', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ updates })
    });
    const json = await res.json();
    if (json.success) {
      alert('Notas guardadas correctamente.');
    } else {
      console.error(json);
      alert('Error guardando notas (ver consola).');
    }
  } catch (err) {
    console.error(err);
    alert('Error guardando notas (ver consola).');
  }
}
