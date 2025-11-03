const horario = [
  ['1', 'Lengua y Literatura', 'Lengua y Literatura', 'Lengua y Literatura', 'Lengua y Literatura', 'Lengua y Literatura'],
  ['2', 'Lengua y Literatura', 'Lengua y Literatura', 'Lengua y Literatura', 'Lengua y Literatura', 'Lengua y Literatura'],
  ['3', 'Matemática', 'Matemática', 'Matemática', 'Matemática', 'Matemática'],
  ['4', 'Matemática', 'Matemática', 'Matemática', 'Matemática', 'Matemática'],
  ['R', 'RECREO', 'RECREO', 'RECREO', 'RECREO', 'RECREO'],
  ['5', 'Ciencias Naturales', 'Ciencias Naturales', 'Ciencias Naturales', 'Educación Cultural y Artística', 'Educación Física'],
  ['6', 'Inglés', 'Inglés', 'Inglés', 'Educación Cultural y Artística', 'Humanismo Integral'],
  ['7', 'Educación', 'Educación', 'Educación', 'Educación', 'Proyecto']
];

// 🔹 Asignamos las horas reales a cada bloque
const horas = {
  1: '7:00 - 8:00',
  2: '8:00 - 9:00',
  3: '9:00 - 10:00',
  4: '10:00 - 11:00',
  5: '11:30 - 12:30',
  6: '12:30 - 1:30',
  7: '1:30 - 2:30'
};

const tbody = document.getElementById('scheduleBody');

// 🔹 Función para aplicar clases según materia
function materiaClase(nombre) {
  nombre = nombre.toLowerCase();
  if (nombre.includes('lengua')) return 'lengua';
  if (nombre.includes('matem')) return 'matematica';
  if (nombre.includes('cienc')) return 'ciencias';
  if (nombre.includes('ingl')) return 'ingles';
  if (nombre.includes('físic')) return 'educacion-fisica';
  if (nombre.includes('artíst')) return 'educacion-artistica';
  if (nombre.includes('human')) return 'humanismo';
  if (nombre.includes('proy')) return 'proyecto';
  return '';
}

// 🔹 Renderizamos la tabla completa
function renderHorario() {
  tbody.innerHTML = '';

  horario.forEach((fila) => {
    const tr = document.createElement('tr');

    // Recreo
    if (fila[0] === 'R') {
      tr.classList.add('recreo');
      const td = document.createElement('td');
      td.colSpan = 6;
      td.textContent = 'RECREO';
      tr.appendChild(td);
      tbody.appendChild(tr);
      return;
    }

    // Celda de hora
    const bloque = document.createElement('td');
    bloque.textContent = horas[fila[0]] || fila[0];
    tr.appendChild(bloque);

    // Materias
    for (let i = 1; i < fila.length; i++) {
      const td = document.createElement('td');
      td.textContent = fila[i];
      td.classList.add(materiaClase(fila[i]));
      tr.appendChild(td);
    }

    tbody.appendChild(tr);
  });
}

renderHorario();
