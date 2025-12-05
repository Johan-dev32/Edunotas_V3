const HORAS = [
  { inicio: "06:45", fin: "07:30" },
  { inicio: "07:30", fin: "08:30" },
  { inicio: "08:30", fin: "09:20" },
  { descanso: true, texto: "DESCANSO" },
  { inicio: "09:50", fin: "10:40" },
  { inicio: "10:40", fin: "11:30" },
  { inicio: "11:30", fin: "12:30" },
  { descanso: true, texto: "ALMUERZO" },
  { inicio: "13:30", fin: "14:20" },
  { inicio: "14:20", fin: "15:30" }
];

const DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"];

const tbody = document.getElementById("scheduleBody");
const tituloCurso = document.getElementById("tituloCurso");

function obtenerClaseAsignatura(nombre) {
  if (!nombre) return '';
  nombre = nombre.toLowerCase();
  
  if (nombre.includes('lengua') || nombre.includes('español') || nombre.includes('lenguaje')) return 'lengua';
  if (nombre.includes('matem')) return 'matematica';
  if (nombre.includes('cienc') || nombre.includes('física') || nombre.includes('química') || nombre.includes('biología')) return 'ciencias';
  if (nombre.includes('ingl')) return 'ingles';
  if (nombre.includes('físic') || nombre.includes('deporte') || nombre.includes('educacion fisica')) return 'educacion-fisica';
  if (nombre.includes('art') || nombre.includes('música') || nombre.includes('danza') || nombre.includes('teatro')) return 'educacion-artistica';
  if (nombre.includes('soci') || nombre.includes('filo') || nombre.includes('etica') || nombre.includes('religión') || nombre.includes('filosofía')) return 'sociales';
  if (nombre.includes('historia') || nombre.includes('geogra')) return 'sociales';
  if (nombre.includes('inform') || nombre.includes('compu') || nombre.includes('tecnol')) return 'tecnologia';
  if (nombre.includes('proy') || nombre.includes('emprend') || nombre.includes('proyecto')) return 'proyecto';
  if (nombre.includes('tutoria') || nombre.includes('orientación') || nombre.includes('convivencia')) return 'tutoria';
  
  return 'otra';
}

function formatearHora(horaStr) {
  if (!horaStr) return '';
  const [hora, minuto] = horaStr.split(':');
  return `${hora.padStart(2, '0')}:${minuto || '00'}`;
}

function renderizarHorario(horario) {
  if (!horario) return;
  
  tituloCurso.textContent = `Curso: ${horario.curso}`;
  
  tbody.innerHTML = '';
  
  HORAS.forEach((franja, index) => {
    const tr = document.createElement('tr');
    
    if (franja.descanso) {
      tr.className = 'recreo';
      const td = document.createElement('td');
      td.colSpan = 6; 
      td.textContent = franja.texto || 'DESCANSO';
      tr.appendChild(td);
      tbody.appendChild(tr);
      return;
    }
    
    const tdHora = document.createElement('td');
    tdHora.textContent = `${formatearHora(franja.inicio)} - ${formatearHora(franja.fin)}`;
    tr.appendChild(tdHora);
    
    DIAS.forEach(dia => {
      const td = document.createElement('td');
      const clasesDia = horario[dia] || [];
      
      const clase = clasesDia.find(c => {
        return c.hora_inicio === franja.inicio || 
               (c.hora_inicio <= franja.inicio && c.hora_fin > franja.inicio);
      });
      
      if (clase) {
        const claseCSS = obtenerClaseAsignatura(clase.asignatura);
        td.className = `bloque-ocupado ${claseCSS}`;
        
        const contenido = document.createElement('div');
        contenido.className = 'clase-contenido';
        
        const titulo = document.createElement('div');
        titulo.className = 'asignatura';
        titulo.textContent = clase.asignatura || '';
        
        const docente = document.createElement('div');
        docente.className = 'docente';
        docente.textContent = clase.docente || '';
        
        const horario = document.createElement('div');
        horario.className = 'horario';
        horario.textContent = `${clase.hora_inicio} - ${clase.hora_fin}`;
        
        contenido.appendChild(titulo);
        contenido.appendChild(docente);
        contenido.appendChild(horario);
        
        td.appendChild(contenido);
      }
      
      tr.appendChild(td);
    });
    
    tbody.appendChild(tr);
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