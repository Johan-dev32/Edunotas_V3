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
  // Asegurarse de que el bloque tenga la clase correcta
  bloque.classList.add('bloque');
  
  // Crear o actualizar el contenido del bloque si es necesario
  let bloqueTexto = bloque.querySelector('.bloque-texto');
  if (!bloqueTexto) {
    // Si no existe el bloque de texto, crearlo
    const materia = bloque.dataset.materia || '';
    const docente = bloque.dataset.docente || '';
    const id_bloque = bloque.dataset.id_bloque || '';
    
    bloque.innerHTML = `
      <div class="bloque-texto" 
           draggable="${editMode}" 
           data-id-bloque="${id_bloque}" 
           data-materia="${materia}" 
           data-docente="${docente}">
        <strong>${materia}</strong><br>${docente}
        <span class="bloque-close">&times;</span>
      </div>`;
    
    bloqueTexto = bloque.querySelector('.bloque-texto');
  } else {
    // Si ya existe, asegurarse de que tenga el botón de cierre
    if (!bloqueTexto.querySelector('.bloque-close')) {
      bloqueTexto.innerHTML += '<span class="bloque-close">&times;</span>';
    }
  }

  // Configurar arrastrable
  bloqueTexto.setAttribute('draggable', editMode);
  
  // Configurar eventos de arrastre
  bloqueTexto.addEventListener('dragstart', e => {
    dragged = bloque;
    setTimeout(() => {
      bloque.style.opacity = '0.4';
    }, 0);
  });

  bloqueTexto.addEventListener('dragend', e => {
    bloque.style.opacity = '1';
    dragged = null;
    guardarBloques();
  });

  // Configurar botón de cierre
  const closeBtn = bloqueTexto.querySelector('.bloque-close');
  if (closeBtn) {
    // Eliminar cualquier evento anterior
    const newCloseBtn = closeBtn.cloneNode(true);
    closeBtn.replaceWith(newCloseBtn);
    
    // Hacer que el botón de cierre sea siempre visible
    newCloseBtn.style.opacity = '0.8';
    newCloseBtn.style.cursor = 'pointer';
    newCloseBtn.style.pointerEvents = 'auto';
    newCloseBtn.style.zIndex = '100';
    
    // Agregar evento de clic
    newCloseBtn.onclick = function(e) {
      e.stopPropagation();
      e.preventDefault();
      if (confirm('¿Estás seguro de que deseas eliminar este bloque?')) {
        bloque.remove();
        guardarBloques();
      }
      return false;
    };
    
    // Efectos hover
    bloque.onmouseenter = function() {
      if (newCloseBtn) {
        newCloseBtn.style.opacity = '1';
        newCloseBtn.style.transform = 'scale(1.2)';
      }
    };
    
    bloque.onmouseleave = function() {
      if (newCloseBtn) {
        newCloseBtn.style.opacity = '0.8';
        newCloseBtn.style.transform = 'scale(1)';
      }
    };
  }
}

// ------------------- Inicializar tabla -------------------
async function initTabla() {
  const tbody = document.querySelector('#horario-table tbody');
  // Limpiar el tbody antes de agregar nuevas filas
  tbody.innerHTML = '';
  
  // Agregar las filas del horario una sola vez
  horas.forEach(h => {
    if (h.descanso) {
      tbody.innerHTML +=
        `<tr>
          <td colspan="6" class="bg-warning fw-bold">DESCANSO</td>
        </tr>`;
    } else {
      tbody.innerHTML +=
        `<tr data-inicio="${h.inicio}" data-fin="${h.fin}">
          <td>${h.inicio} - ${h.fin}</td>
          <td data-dia="Lunes" data-hora="${h.inicio.trim()}"></td>
          <td data-dia="Martes" data-hora="${h.inicio.trim()}"></td>
          <td data-dia="Miércoles" data-hora="${h.inicio.trim()}"></td>
          <td data-dia="Jueves" data-hora="${h.inicio.trim()}"></td>
          <td data-dia="Viernes" data-hora="${h.inicio.trim()}"></td>
        </tr>`;
    }
  });

  // Configurar eventos de arrastrar y soltar
  function configurarEventos() {
    document.querySelectorAll('#horario-table td, #fuera-tabla').forEach(td => {
      // Remover eventos anteriores para evitar duplicados
      const newTd = td.cloneNode(true);
      td.parentNode.replaceChild(newTd, td);
      
      newTd.addEventListener('dragover', e => e.preventDefault());
      newTd.addEventListener('drop', e => {
        e.preventDefault();
        if (!editMode || !dragged) return;
        if (newTd.querySelector('.bloque') && newTd.id !== 'fuera-tabla') return;
        newTd.appendChild(dragged);
        guardarBloques();
      });

      newTd.addEventListener('dblclick', () => {
        if (!editMode) return;
        if (!newTd.dataset.dia) return;
        crearBloque(newTd);
      });
    });
  }
  
  configurarEventos();
  
  // Cargar bloques solo si no se han cargado antes
  if (!window._bloquesCargados) {
    window._bloquesCargados = true;
    await cargarBloques();
    // Volver a configurar eventos después de cargar bloques
    configurarEventos();
  }
}

// ------------------- Cargar bloques desde DB -------------------
async function cargarBloques() {
  try {
    const resp = await fetch(`/administrador/api/curso/${curso_id}/bloques_db`);
    const data = await resp.json();
    console.log("Datos recibidos del servidor:", data);

    // Primero, limpiar todos los bloques existentes
    document.querySelectorAll('#horario-table .bloque').forEach(bloque => {
      bloque.remove();
    });

    const diasMap = { 
      lun: "Lunes", mar: "Martes", mie: "Miércoles", 
      jue: "Jueves", vie: "Viernes" 
    };
    
    // Mapa de horas
    const horaIndexMap = { 
      1: "06:45", 2: "07:30", 3: "08:30", 4: "09:50", 
      5: "10:40", 6: "11:30", 7: "13:30", 8: "14:20"
    };

    // Crear un array para almacenar promesas de creación de bloques
    const promesas = [];

    data.forEach(b => {
      try {
        const dia = diasMap[b.dia] || b.dia || b.Dia;
        
        // Determinar la hora del bloque
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

        // Crear el bloque directamente en lugar de usar crearBloque
        const bloque = document.createElement('div');
        bloque.className = 'bloque';
        
        const materia = b.materia || b.Materia || (b.asignatura ? b.asignatura.Nombre : '');
        const docente = b.docente || b.Docente || (b.docente_nombre ? b.docente_nombre : '');
        const id_bloque = b.id_bloque || b.ID_Bloque || b.id || '';
        
        bloque.innerHTML = `
          <div class="bloque-texto" 
               draggable="${editMode}" 
               data-id-bloque="${id_bloque}" 
               data-materia="${materia}" 
               data-docente="${docente}">
            <strong>${materia}</strong><br>${docente}
            <span class="bloque-close">&times;</span>
          </div>`;
        
        celda.appendChild(bloque);
        
        // Activar el bloque recién creado
        activarBloque(bloque);
        
      } catch (error) {
        console.error('Error al procesar bloque:', b, error);
      }
    });
  } catch (error) {
    console.error('Error al cargar bloques:', error);
  }
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
      const id_bloque = Object.entries(horaIndexMap).find(([_, h]) => h === hora)?.[0] || null;

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