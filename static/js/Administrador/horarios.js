let editMode = false;
let dragged = null;
const curso_id = document.body.dataset.cursoId;

// horas fijas reales
const horas = [
  {inicio:"06:45", fin:"07:30"},
  {inicio:"07:30", fin:"08:30"},
  {inicio:"08:30", fin:"09:20"},
  {descanso:true},
  {inicio:"09:50", fin:"10:40"},
  {inicio:"10:40", fin:"11:30"},
  {inicio:"11:30", fin:"12:30"},
  {descanso:true},
  {inicio:"13:30", fin:"14:20"},
  {inicio:"14:20", fin:"15:30"}
];

// ------------------- Toggle modo edición -------------------
function toggleEditMode() {
    editMode = !editMode;
    const btn = document.querySelector('.btn-success');
    btn.innerHTML = editMode
        ? '<i class="bi bi-pencil-square"></i> Editando'
        : '<i class="bi bi-pencil-square"></i> Modo Edición';
    btn.classList.toggle('btn-warning', editMode);

    document.querySelectorAll('.bloque-texto').forEach(b => {
        b.setAttribute('draggable', editMode);
    });

    document.getElementById('fuera-tabla').style.display = editMode ? 'flex' : 'none';
}

// ------------------- Crear bloque -------------------
function crearBloque(celda, data = null) {
    const bloque = document.createElement('div');
    bloque.className = 'bloque';

    if (data) {
        bloque.innerHTML = `<div class="bloque-texto" draggable="${editMode}" 
                                data-id="${data.id}">
                                <strong>${data.materia}</strong><br>
                                ${data.docente}<br>
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


                    bloque.innerHTML = `<div class="bloque-texto" draggable="${editMode}">
                        <strong>${materia}</strong><br>${docente}<br>
                        <span class="bloque-close">&times;</span>
                    </div>`;
                    activarBloque(bloque);
                    guardarBloques();
                }
            });
        });

        closeBtn.addEventListener('click', () => {
            bloque.remove();
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
    bloqueTexto.addEventListener('dragend', e => dragged = null);

    const closeBtn = bloqueTexto.querySelector('.bloque-close');
    if (closeBtn) closeBtn.addEventListener('click', () => bloque.remove());
}

// ------------------- Inicializar tabla -------------------
async function initTabla() {
    const tbody = document.querySelector('#horario-table tbody');
    tbody.innerHTML = '';

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
              <td data-dia="Lunes" data-hora="${h.inicio}"></td>
              <td data-dia="Martes" data-hora="${h.inicio}"></td>
              <td data-dia="Miércoles" data-hora="${h.inicio}"></td>
              <td data-dia="Jueves" data-hora="${h.inicio}"></td>
              <td data-dia="Viernes" data-hora="${h.inicio}"></td>
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
        });

        td.addEventListener('dblclick', () => {
            if (!editMode) return;
            if (!td.dataset.dia) return;
            crearBloque(td);
        });
    });

    cargarBloques();
}

// ------------------- Cargar bloques desde DB -------------------
async function cargarBloques() {
    const resp = await fetch(`/api/curso/${curso_id}/bloques_db`);
    const data = await resp.json();
    console.log("DATA:", data);
    data.forEach(b => {
        const celda = document.querySelector(
            `td[data-dia="${b.dia}"][data-hora="${b.hora_inicio}"]`
        );
        if (celda) crearBloque(celda, b);
    });
}

// ------------------- Guardar bloques en DB -------------------
async function guardarBloques() {
    if (!editMode) return;

    const bloques = [];
    document.querySelectorAll('.bloque').forEach(b => {
        const parent = b.parentElement;
        const bloqueTexto = b.querySelector('.bloque-texto');
        if (!bloqueTexto) return;

        let dia = parent.dataset.dia || null;
        let hora = parent.dataset.hora || null;

        let contenido = bloqueTexto.innerHTML.replace('<span class="bloque-close">&times;</span>', '').trim();
        let partes = contenido.split('<br>');
        let materia = partes[0].replace(/<strong>|<\/strong>/g, '');
        let docente = partes[1] || '';

        bloques.push({ dia, hora, materia, docente, id: bloqueTexto.dataset.id || null, curso_id: curso_id });
    });

    await fetch('/guardar_horario', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(bloques)
    });
}

// ------------------- Inicializar asignaciones -------------------
document.querySelectorAll('.bloque-asignacion').forEach(bloque => {
    bloque.classList.add('bloque');
    const contenido = `<div class="bloque-texto" draggable="${editMode}">
        ${bloque.dataset.materia} - ${bloque.dataset.docente}
        <span class="bloque-close">&times;</span>
    </div>`;
    bloque.innerHTML = contenido;
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