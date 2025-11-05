const curso_id = document.body.dataset.cursoId;

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

const dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"];
const tbody = document.getElementById("scheduleBody");

// 🔹 Renderizar estructura vacía
function renderTablaVacia() {
  tbody.innerHTML = "";
  horas.forEach(h => {
    if (h.descanso) {
      const tr = document.createElement("tr");
      tr.classList.add("recreo");
      const td = document.createElement("td");
      td.colSpan = 6;
      td.textContent = "RECREO";
      tr.appendChild(td);
      tbody.appendChild(tr);
    } else {
      const tr = document.createElement("tr");
      const th = document.createElement("td");
      th.textContent = `${h.inicio} - ${h.fin}`;
      tr.appendChild(th);

      dias.forEach(dia => {
        const td = document.createElement("td");
        td.dataset.dia = dia;
        td.dataset.hora = h.inicio;
        tr.appendChild(td);
      });

      tbody.appendChild(tr);
    }
  });
}

// 🔹 Aplicar color según materia
function materiaClase(nombre) {
  if (!nombre) return '';
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

// 🔹 Cargar desde BD
async function cargarHorario() {
  try {
    const resp = await fetch(`/administrador/api/curso/${curso_id}/bloques_db`);
    const data = await resp.json();

    const tbody = document.getElementById('scheduleBody');
    tbody.innerHTML = "";

    // Definir las horas visibles (las mismas del administrador)
    const horas = ["06:45", "07:30", "08:30", "09:50", "10:40", "11:30", "13:30", "14:20", "15:20"];
    const dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"];

    // Crear una fila por hora
    horas.forEach(hora => {
      const tr = document.createElement('tr');

      const tdHora = document.createElement('td');
      tdHora.textContent = hora;
      tr.appendChild(tdHora);

      dias.forEach(dia => {
        const td = document.createElement('td');
        const bloque = data.find(b => b.dia === dia && b.hora_inicio === hora);

        if (bloque) {
          td.textContent = `${bloque.materia} - ${bloque.docente}`;
          td.classList.add('bloque-ocupado');
        }

        tr.appendChild(td);
      });

      tbody.appendChild(tr);
    });

  } catch (err) {
    console.error("❌ Error al cargar horario:", err);
  }
}

cargarHorario();