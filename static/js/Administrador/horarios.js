let editMode = false;
let dragged = null;
const curso_id = document.body.dataset.cursoId;
let saveTimeout;

// horas fijas reales
const horas = [
  { inicio: "06:45", fin: "07:30" },
  { inicio: "07:30", fin: "08:30" },
  { inicio: "08:30", fin: "09:20" },
  { descanso: true },
  { inicio: "09:50", fin: "10:40" },
  { inicio: "10:40", fin: "11:30" },
  { inicio: "11:30", fin: "12:30" },
  { descanso: true },
  { inicio: "13:30", fin: "14:20" },
  { inicio: "14:20", fin: "15:30" }
];

// ------------------- Toggle modo edición -------------------
function guardarBloquesDebounced() {
  clearTimeout(saveTimeout);
  saveTimeout = setTimeout(() => guardarBloques(), 500);
}

function toggleEditMode() {
  editMode = !editMode;

  const btn = document.querySelector('.btn-success');
  if (btn) {
    btn.innerHTML = editMode
      ? '<i class="bi bi-pencil-square"></i> Editando'
      : '<i class="bi bi-pencil-square"></i> Modo Edición';
    btn.classList.toggle('btn-warning', editMode);
  }

  // habilitar o deshabilitar arrastre
  document.querySelectorAll('.bloque-texto').forEach(b => {
    b.setAttribute('draggable', editMode);
  });

  // mostrar/ocultar contenedor fuera de la tabla si existe
  const fueraTabla = document.getElementById('fuera-tabla');
  if (fueraTabla) {
    fueraTabla.style.display = editMode ? 'flex' : 'none';
  }

  // 💾 Guardar solo cuando se desactiva el modo edición
  if (!editMode) guardarBloquesDebounced();
}
// ------------------- Crear bloque -------------------
function crearBloque(celda, data = null) {
  const bloque = document.createElement('div');
  bloque.className = 'bloque';

  if (data) {
    bloque.innerHTML = `
      <div class="bloque-texto" 
           draggable="${editMode}" 
           data-id-bloque="${data.id_bloque || ''}" 
           data-materia="${data.materia}" 
           data-docente="${data.docente}">
           <strong>${data.materia}</strong><br>${data.docente}
           <span class="bloque-close">&times;</span>
      </div>`;
    activarBloque(bloque);
  } else {
    bloque.innerHTML = `
      <input type="text" placeholder="Materia" class="bloque-input bloque-materia">
      <input type="text" placeholder="Docente" class="bloque-input bloque-docente">
      <span class="bloque-close">&times;</span>
    `;
    const materiaInput = bloque.querySelector('.bloque-materia');
    const docenteInput = bloque.querySelector('.bloque-docente');
    const closeBtn = bloque.querySelector('.bloque-close');

    [materiaInput, docenteInput].forEach(input => {
      input.addEventListener('keypress', e => {
        if (e.key === 'Enter') {
          const materia = materiaInput.value.trim();
          const docente = docenteInput.value.trim();

          bloque.innerHTML = `<div class="bloque-texto" draggable="${editMode}"
              data-id-bloque=""
              data-materia="${materia}" 
              data-docente="${docente}">
              <strong>${materia}</strong><br>${docente}
              <span class="bloque-close">&times;</span>
          </div>`;
          activarBloque(bloque);
          guardarBloques();
        }
      });
    });

    closeBtn.addEventListener('click', () => {
      bloque.remove();
      guardarBloques();
    });
  }

  celda.appendChild(bloque);
}
// ------------------- Activar drag & drop -------------------
function activarBloque(bloque) {
  const bloqueTexto = bloque.querySelector('.bloque-texto');
  if (!bloqueTexto) return;

  bloqueTexto.setAttribute('draggable', editMode);

  bloqueTexto.addEventListener('dragstart', e => dragged = bloque);
  bloqueTexto.addEventListener('dragend', e => {
    dragged = null;
    guardarBloques(); // 💾 guarda automáticamente al soltar
  });

  const closeBtn = bloqueTexto.querySelector('.bloque-close');
  if (closeBtn) closeBtn.addEventListener('click', () => {
    bloque.remove();
    guardarBloques();
  });
}

// ------------------- Inicializar tabla -------------------
async function initTabla() {
  const tbody = document.querySelector('#horario-table tbody');
  if (!tbody.hasChildNodes()) {
    horas.forEach(h => {
      if (h.descanso) {
        tbody.innerHTML += `<tr><td colspan="6" class="bg-warning fw-bold">DESCANSO</td></tr>`;
      } else {
        tbody.innerHTML += `
          <tr data-inicio="${h.inicio}" data-fin="${h.fin}">
            <td>${h.inicio} - ${h.fin}</td>
            <td data-dia="Lunes" data-hora="${h.inicio.trim()}"></td>
            <td data-dia="Martes" data-hora="${h.inicio.trim()}"></td>
            <td data-dia="Miércoles" data-hora="${h.inicio.trim()}"></td>
            <td data-dia="Jueves" data-hora="${h.inicio.trim()}"></td>
            <td data-dia="Viernes" data-hora="${h.inicio.trim()}"></td>
          </tr>`;
      }
    });
  }

  horas.forEach(h => {
    if (h.descanso) {
      tbody.innerHTML += `
        <tr>
          <td colspan="6" class="bg-warning fw-bold">DESCANSO</td>
        </tr>`;
    } else {
      tbody.innerHTML += `
        <tr data-inicio="${h.inicio}" data-fin="${h.fin}">
          <td>${h.inicio} - ${h.fin}</td>
          <td data-dia="Lunes" data-hora="${h.inicio.trim()}"></td>
          <td data-dia="Martes" data-hora="${h.inicio.trim()}"></td>
          <td data-dia="Miércoles" data-hora="${h.inicio.trim()}"></td>
          <td data-dia="Jueves" data-hora="${h.inicio.trim()}"></td>
          <td data-dia="Viernes" data-hora="${h.inicio.trim()}"></td>
        </tr>`;
    }
  });

  // Drag & drop en celdas
  document.querySelectorAll('#horario-table td, #fuera-tabla').forEach(td => {
    td.addEventListener('dragover', e => e.preventDefault());
    td.addEventListener('drop', e => {
      e.preventDefault();
      if (!editMode || !dragged) return;
      if (td.querySelector('.bloque') && td.id !== 'fuera-tabla') return;
      td.appendChild(dragged);
      guardarBloques(); // 💾 guarda cada vez que sueltas
    });

    td.addEventListener('dblclick', () => {
      if (!editMode) return;
      if (!td.dataset.dia) return;
      crearBloque(td);
    });
  });

  if (!window._bloquesCargados) {
  window._bloquesCargados = true;
  cargarBloques();
}
}

// ------------------- Cargar bloques desde DB -------------------
async function cargarBloques() {
  const resp = await fetch(`/administrador/api/curso/${curso_id}/bloques_db`);
  const data = await resp.json();
  console.log("DATA:", data);

  // Limpia bloques viejos
  document.querySelectorAll('#horario-table td .bloque').forEach(n => n.remove());

  const diasMap = { 
    lun: "Lunes", mar: "Martes", mie: "Miércoles", 
    jue: "Jueves", vie: "Viernes" 
  };
  
  // 🔹 Asegúrate de incluir las 9 horas (coinciden con tu tabla)
  const horaIndexMap = { 
    1: "06:45", 2: "07:30", 3: "08:30", 4: "09:50", 
    5: "10:40", 6: "11:30", 7: "13:30", 8: "14:20"
  };

  data.forEach(b => {
    const dia = diasMap[b.dia] || b.dia || b.Dia;
    
    // 🔹 Prioriza `b.hora_inicio`, luego `b.id_bloque`, luego `b.hora`
    let hora = null;
    if (b.hora_inicio) {
      hora = b.hora_inicio;
    } else if (b.id_bloque) {
      hora = horaIndexMap[b.id_bloque] || null;
    } else if (typeof b.hora === 'number') {
      hora = horaIndexMap[b.hora] || null;
    } else {
      hora = b.hora || b.HoraInicio;
    }

    if (!dia || !hora) {
      console.warn("Bloque sin dia/hora válido:", b);
      return;
    }

    const celda = document.querySelector(`td[data-dia="${dia}"][data-hora="${hora.trim()}"]`);
    if (!celda) {
      console.warn(`No existe celda para ${dia} ${hora} (id_bloque=${b.id_bloque})`);
      return;
    }


    if (!celda.querySelector('.bloque')) {
    crearBloque(celda, {
      id_bloque: b.id_bloque || b.ID_Bloque || b.id || '',
      materia: b.materia || b.Materia || (b.asignatura ? b.asignatura.Nombre : ''),
      docente: b.docente || b.Docente || (b.docente_nombre ? b.docente_nombre : '')
    });
  }
  });
}
// ------------------- Guardar bloques en DB -------------------

async function guardarBloques() {
  const bloques = [];

  document.querySelectorAll('.bloque').forEach(b => {
    const parent = b.parentElement;
    const bloqueTexto = b.querySelector('.bloque-texto');
    if (!bloqueTexto || !parent.dataset) return;

    const materia = bloqueTexto.dataset.materia;
    const docente = bloqueTexto.dataset.docente;
    const dia = parent.dataset.dia;
    const hora = parent.dataset.hora;
    const fila = parent.closest('tr');
    const hora_fin = fila ? fila.dataset.fin : null;

    if (dia && hora) {

      // 🔹 Mapa de hora → ID_Bloque (según tu tabla Bloques)
      const horaIndexMap = {
        "06:45": 1,
        "07:30": 2,
        "08:30": 3,
        "09:50": 4,
        "10:40": 5,
        "11:30": 6,
        "13:30": 7,
        "14:20": 8
      };

      // 🔹 Convertimos la hora actual a ID_Bloque válido
      const id_bloque = null;

      bloques.push({
        id_bloque,   // 👈 ahora sí manda un ID real que existe
        dia,
        hora,
        hora_fin,
        materia,
        docente,
        curso_id
      });
    }
  });

  console.log("📤 Enviando bloques al backend:", bloques);

  const resp = await fetch(`/administrador/guardar_horario/${curso_id}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ bloques })
  });

  const data = await resp.json();
  if (data.ok) {
    console.log("✅ Horario guardado correctamente");
  } else {
    console.error("❌ Error al guardar:", data.error);
  }
}
// ------------------- Inicializar asignaciones -------------------
document.querySelectorAll('.bloque-asignacion').forEach(bloque => {
  bloque.classList.add('bloque');
  bloque.innerHTML = `
    <div class="bloque-texto" draggable="${editMode}"
         data-materia="${bloque.dataset.materia}"
         data-docente="${bloque.dataset.docente}">
         <strong>${bloque.dataset.materia}</strong><br>${bloque.dataset.docente}
         <span class="bloque-close">&times;</span>
    </div>`;
  activarBloque(bloque);
});

// ------------------- PDF -------------------
function generarPDF(curso_id) {
  const contenido = document.getElementById('horario-contenido');
  html2pdf().set({
    margin: 0.2,
    filename: `horario_${curso_id}.pdf`,
    html2canvas: { scale: 2 },
    jsPDF: { orientation: 'landscape' }
  }).from(contenido).save();
}



// ------------------- Ejecutar -------------------
document.addEventListener('DOMContentLoaded', () => initTabla());
