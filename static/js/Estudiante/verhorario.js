const HORAS = [
  { inicio: "06:45", fin: "07:30" },
  { inicio: "07:30", fin: "08:30" },
  { inicio: "08:30", fin: "09:20" },
  { descanso: true, texto: "DESCANSO" },
  { inicio: "09:50", fin: "10:40" },
  { inicio: "10:40", fin: "11:30" },
  { inicio: "11:30", fin: "12:30" },
  { descanso: true, texto: "DESCANSO" },
  { inicio: "13:30", fin: "14:20" },
  { inicio: "14:20", fin: "15:30" }
];

const DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"];

const tbody = document.getElementById("scheduleBody");
const tituloCurso = document.getElementById("tituloCurso");

function obtenerClaseAsignatura(nombre) {
  if (!nombre) return 'otra';
  nombre = nombre.toLowerCase();
  
  if (nombre.includes('lengua') || nombre.includes('español') || nombre.includes('lenguaje')) return 'lengua';
  if (nombre.includes('matem')) return 'matematica';
  if (nombre.includes('cienc') || nombre.includes('física') || nombre.includes('química') || nombre.includes('biología')) return 'ciencias';
  if (nombre.includes('ingl')) return 'ingles';
  if (nombre.includes('físic') || nombre.includes('deporte') || nombre.includes('educacion fisica')) return 'educacion-fisica';
  if (nombre.includes('art') || nombre.includes('música') || nombre.includes('danza') || nombre.includes('teatro')) return 'educacion-artistica';
  if (nombre.includes('soci') || nombre.includes('historia') || nombre.includes('geogra')) return 'sociales';
  if (nombre.includes('inform') || nombre.includes('compu') || nombre.includes('tecnol')) return 'tecnologia';
  if (nombre.includes('proy') || nombre.includes('emprend') || nombre.includes('proyecto')) return 'proyecto';
  if (nombre.includes('tutoria') || nombre.includes('orientación') || nombre.includes('convivencia')) return 'tutoria';
  if (nombre.includes('ética') || nombre.includes('religión') || nombre.includes('filosofía')) return 'etica';
  
  return 'otra';
}

function formatearHora(horaStr) {
  if (!horaStr) return '';
  const [hora, minuto] = horaStr.split(':');
  return `${hora.padStart(2, '0')}:${minuto || '00'}`;
}

function renderizarHorario(horario) {
  console.log('Datos del horario recibidos:', horario);
  if (!horario) {
    console.error('No se recibió el horario');
    return;
  }
  
  tituloCurso.textContent = `Curso: ${horario.curso || 'No asignado'}`;
  tbody.innerHTML = '';

  // Crear una matriz para representar la tabla
  const tabla = Array(HORAS.length).fill().map(() => 
    Array(DIAS.length + 1).fill(null)  // +1 para la columna de horas
  );

  // Llenar la primera columna con las horas
  HORAS.forEach((franja, i) => {
    if (!franja.descanso) {
      tabla[i][0] = {
        tipo: 'hora',
        texto: `${formatearHora(franja.inicio)} - ${formatearHora(franja.fin)}`
      };
    }
  });

  // Llenar la tabla con las clases
  DIAS.forEach((dia, diaIndex) => {
    const clasesDia = horario.horario[dia] || [];
    console.log(`Procesando día ${dia} (índice ${diaIndex}):`, clasesDia);
    
    clasesDia.forEach(clase => {
      const inicioIndex = HORAS.findIndex(h => 
        !h.descanso && h.inicio === clase.hora_inicio
      );
      
      if (inicioIndex !== -1) {
        const finIndex = HORAS.findIndex(h => 
          !h.descanso && h.fin === clase.hora_fin
        );
        
        if (finIndex !== -1) {
          const duracion = finIndex - inicioIndex + 1;
          const claseCSS = obtenerClaseAsignatura(clase.asignatura);
          
          // Asegurarse de que el índice del día sea correcto
          const columnaDia = diaIndex + 1; // +1 por la columna de horas
          
          console.log(`Asignando ${clase.asignatura} a ${dia} (columna ${columnaDia}), fila ${inicioIndex} a ${finIndex}`);
          
          // Solo asignar si la celda está vacía
          if (!tabla[inicioIndex][columnaDia]) {
            tabla[inicioIndex][columnaDia] = {
              tipo: 'clase',
              clase: clase,
              duracion: duracion,
              claseCSS: claseCSS
            };
            
            // Marcar las celdas ocupadas
            for (let i = inicioIndex + 1; i <= finIndex; i++) {
              if (!tabla[i]) continue;
              if (!tabla[i][columnaDia]) {
                tabla[i][columnaDia] = { tipo: 'ocupada' };
              }
            }
          }
        }
      }
    });
  });

  // Renderizar la tabla
  tabla.forEach((fila, filaIndex) => {
    if (HORAS[filaIndex]?.descanso) {
      // Si es un descanso, crear una fila de descanso
      const tr = document.createElement('tr');
      const td = document.createElement('td');
      td.colSpan = DIAS.length + 1;
      td.className = 'descanso';
      td.textContent = HORAS[filaIndex].texto || 'DESCANSO';
      tr.appendChild(td);
      tbody.appendChild(tr);
    } else {
      const tr = document.createElement('tr');
      
      fila.forEach((celda, colIndex) => {
        if (celda === null) {
          // Celda vacía
          const td = document.createElement('td');
          tr.appendChild(td);
        } else if (celda.tipo === 'hora') {
          // Celda de hora
          const td = document.createElement('td');
          td.className = 'hora';
          td.textContent = celda.texto;
          tr.appendChild(td);
        } else if (celda.tipo === 'clase') {
          // Celda de clase
          const td = document.createElement('td');
          td.rowSpan = celda.duracion;
          td.className = 'clase';
          td.innerHTML = `
            <div class="bloque-horario ${celda.claseCSS}">
              <div class="asignatura">${celda.clase.asignatura}</div>
              <div class="docente">${celda.clase.docente}</div>
              <div class="horario">${celda.clase.hora_inicio} - ${celda.clase.hora_fin}</div>
            </div>
          `;
          tr.appendChild(td);
        }
        // Las celdas 'ocupadas' no se renderizan
      });
      
      if (tr.children.length > 0) {
        tbody.appendChild(tr);
      }
    }
  });
}

async function cargarHorario() {
  try {
    // Mostrar estado de carga
    tbody.innerHTML = `
      <tr>
        <td colspan="6" class="text-center py-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Cargando...</span>
          </div>
          <p class="mt-2 mb-0">Cargando horario...</p>
        </td>
      </tr>`;

    const response = await fetch('/estudiante/api/mi-horario');
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || 'Error al cargar el horario');
    }
    
    const data = await response.json();
    
    if (data.error) {
      throw new Error(data.error);
    }
    
    renderizarHorario(data);
    
  } catch (error) {
    console.error('Error al cargar el horario:', error);
    mostrarError(error.message || 'Error al cargar el horario. Por favor, intente nuevamente.');
  }
}

function mostrarError(mensaje) {
  tbody.innerHTML = `
    <tr>
      <td colspan="6" class="text-center text-danger py-4">
        <i class="bi bi-exclamation-triangle-fill me-2"></i>
        ${mensaje}
      </td>
    </tr>`;
}

// Iniciar la carga del horario cuando el documento esté listo
document.addEventListener('DOMContentLoaded', cargarHorario);