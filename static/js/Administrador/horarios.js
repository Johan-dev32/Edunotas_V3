let editMode = false;
let dragged = null;
const curso_id = document.body.dataset.cursoId;

// Toggle modo edición
function toggleEditMode() {
    editMode = !editMode;
    const btn = document.querySelector('.btn-success');
    btn.innerHTML = editMode
        ? '<i class="bi bi-pencil-square"></i> Editando'
        : '<i class="bi bi-pencil-square"></i> Modo Edición';
    btn.classList.toggle('btn-warning', editMode);

    document.querySelectorAll('.bloque').forEach(b => {
        const bt = b.querySelector('.bloque-texto');
        if (bt) bt.setAttribute('draggable', editMode);
    });

    const fueraTabla = document.getElementById('fuera-tabla');
    fueraTabla.style.display = editMode ? 'flex' : 'none';
}

// Cargar bloques desde localStorage
function cargarBloques() {
    const data = JSON.parse(localStorage.getItem(`horario_${curso_id}`) || '[]');
    data.forEach(b => {
        let celda;
        if (b.fuera) celda = document.getElementById('fuera-tabla');
        else celda = document.querySelector(`td[data-dia="${b.dia}"][data-hora="${b.hora}"]`);
        if (celda) crearBloque(celda, b);
    });
}

// Guardar bloques en localStorage
function guardarBloques() {
    const data = [];
    document.querySelectorAll('.bloque').forEach(b => {
        const parent = b.parentElement;
        const bloqueTexto = b.querySelector('.bloque-texto');
        if (!bloqueTexto) return;
        let dia = parent.dataset.dia || 'fuera';
        let hora = parent.dataset.hora || 'fuera';
        data.push({
            dia,
            hora,
            contenido: bloqueTexto.innerHTML.replace('<span class="bloque-close">&times;</span>', '').trim(),
            fuera: parent.id === 'fuera-tabla'
        });
    });
    localStorage.setItem(`horario_${curso_id}`, JSON.stringify(data));
}

// Crear bloque
function crearBloque(celda, data = null) {
    if (!editMode && !data) return;
    if (!data && celda.querySelector('.bloque')) return; // Bloque único por celda

    const bloque = document.createElement('div');
    bloque.className = 'bloque';

    if (data) {
        bloque.innerHTML = `<div class="bloque-texto" draggable="${editMode}">
            ${data.contenido}
            <span class="bloque-close">&times;</span>
        </div>`;
        activarBloque(bloque);
    } else {
        bloque.innerHTML = `
            <input type="text" placeholder="Materia" class="bloque-input bloque-materia">
            <input type="text" placeholder="Docente" class="bloque-input bloque-docente">
            <input type="text" placeholder="Aula" class="bloque-input bloque-aula">
            <span class="bloque-close">&times;</span>
        `;
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
                        <div class="bloque-texto" draggable="${editMode}">
                            <strong>${materia}</strong><br>
                            ${docente}<br>
                            Aula: ${aula}
                            <span class="bloque-close">&times;</span>
                        </div>
                    `;
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

// Activar drag & drop y botón cerrar
function activarBloque(bloque) {
    const bloqueTexto = bloque.querySelector('.bloque-texto');
    if (!bloqueTexto) return;

    bloqueTexto.setAttribute('draggable', editMode);

    bloqueTexto.addEventListener('dragstart', e => dragged = bloque);
    bloqueTexto.addEventListener('dragend', e => {
        dragged = null;
        guardarBloques();
    });

    // Cada vez que se crea o mueve, reactivamos botón de cierre
    const closeBtn = bloqueTexto.querySelector('.bloque-close');
    if (closeBtn) {
        closeBtn.addEventListener('click', () => {
            bloque.remove();
            guardarBloques();
        });
    }
}

// Drag & Drop de celdas
document.querySelectorAll('#horario-table td, #fuera-tabla').forEach(td => {
    td.addEventListener('dblclick', () => {
        // Solo permitir celdas que tengan data-dia
        if (!td.dataset.dia || td.classList.contains('recreo-cell')) return;
        crearBloque(td);
    });

    td.addEventListener('dragover', e => e.preventDefault());
    td.addEventListener('drop', e => {
        e.preventDefault();
        if (!editMode || !dragged) return;
        if (td.querySelector('.bloque') && td.id !== 'fuera-tabla') return;
        td.appendChild(dragged);
        // Reasignar evento de cierre por si se movió
        activarBloque(dragged);
        guardarBloques();
    });
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

// Inicialización
cargarBloques();
