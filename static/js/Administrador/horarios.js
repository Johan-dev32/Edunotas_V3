let editMode = false;
let dragged = null;

// Toggle modo edición
function toggleEditMode() {
    editMode = !editMode;
    const btn = document.querySelector('.btn-success');
    btn.innerHTML = editMode ? '<i class="bi bi-pencil-square"></i> Editando' : '<i class="bi bi-pencil-square"></i> Modo Edición';
    btn.classList.toggle('btn-warning', editMode);

    document.querySelectorAll('.bloque').forEach(b => {
        b.setAttribute('draggable', editMode);
    });
}

// Drag & Drop
function dragStart(e) {
    dragged = e.currentTarget;
    setTimeout(() => dragged.classList.add('dragging'), 0);
}

function dragEnd(e) {
    e.currentTarget.classList.remove('dragging');
    dragged = null;
}

function dragOver(e) {
    e.preventDefault();
}

function drop(e) {
    e.preventDefault();
    if (!editMode || !dragged) return;

    const target = e.currentTarget;

    // Barra puede tener varios bloques
    if (target.id === 'fuera-tabla') {
        target.appendChild(dragged);
        return;
    }

    // Solo 1 bloque por celda
    if (target.tagName === 'TD' && target.querySelector('.bloque')) return;

    if (target.tagName === 'TD') {
        target.appendChild(dragged);
    }
}

// Crear bloque
function crearBloque(celda) {
    if (!editMode || celda.querySelector('.bloque')) return;

    const bloque = document.createElement('div');
    bloque.className = 'bloque';
    bloque.innerHTML = `
        <input type="text" placeholder="Materia" class="bloque-input bloque-materia">
        <input type="text" placeholder="Docente" class="bloque-input bloque-docente">
        <input type="text" placeholder="Aula" class="bloque-input bloque-aula">
        <span class="bloque-close">&times;</span>
    `;
    celda.appendChild(bloque);

    const materiaInput = bloque.querySelector('.bloque-materia');
    const docenteInput = bloque.querySelector('.bloque-docente');
    const aulaInput = bloque.querySelector('.bloque-aula');
    const closeBtn = bloque.querySelector('.bloque-close');

    materiaInput.addEventListener('input', e => e.target.value = e.target.value.replace(/[^a-zA-Z\s]/g, ''));
    docenteInput.addEventListener('input', e => e.target.value = e.target.value.replace(/[^a-zA-Z\s]/g, ''));

    [materiaInput, docenteInput, aulaInput].forEach(input => {
        input.addEventListener('keypress', e => {
            if (e.key === 'Enter') {
                const materia = materiaInput.value.trim();
                const docente = docenteInput.value.trim();
                const aula = aulaInput.value.trim();

                bloque.innerHTML = `
                    <div class="bloque-texto">
                        <strong>${materia}</strong><br>
                        ${docente}<br>
                        Aula: ${aula}
                        <span class="bloque-close">&times;</span>
                    </div>
                `;

                const bloqueFinal = bloque.querySelector('.bloque-texto');
                bloqueFinal.setAttribute('draggable', editMode);
                bloqueFinal.addEventListener('dragstart', dragStart);
                bloqueFinal.addEventListener('dragend', dragEnd);

                bloqueFinal.querySelector('.bloque-close').addEventListener('click', () => bloque.remove());
            }
        });
    });

    bloque.setAttribute('draggable', editMode);
    bloque.addEventListener('dragstart', dragStart);
    bloque.addEventListener('dragend', dragEnd);
    closeBtn.addEventListener('click', () => bloque.remove());
}

// Crear bloque con doble click
document.querySelectorAll('#horario-table td, #fuera-tabla').forEach(td => {
    td.addEventListener('dblclick', () => {
        if (!td.classList.contains('recreo-cell')) crearBloque(td);
    });
    td.addEventListener('dragover', dragOver);
    td.addEventListener('drop', drop);
});

// PDF
function generarPDF(curso_id) {
    const contenido = document.getElementById('horario-contenido');
    html2pdf().set({
        margin: 0.2,
        filename: `horario_${curso_id}.pdf`,
        html2canvas: { scale: 2 },
        jsPDF: { orientation: 'landscape' }
    }).from(contenido).save();
}
