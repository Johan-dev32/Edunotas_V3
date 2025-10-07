const estudiantesEjemplo = [
  { id: 1, nombre: 'Juan Pérez' },
  { id: 2, nombre: 'María López' },
  { id: 3, nombre: 'Pedro Gómez' },
  { id: 4, nombre: 'Ana Rodríguez' },
  { id: 5, nombre: 'Luis Martínez' },
  { id: 6, nombre: 'Camila Torres' },
  { id: 7, nombre: 'Andrés Ramírez' },
  { id: 8, nombre: 'Valentina Herrera' },
  { id: 9, nombre: 'Santiago Gómez' },
  { id: 10, nombre: 'Laura Castillo' }
];


const tablaBody = document.querySelector('#tablaAsistencia tbody');
const fechaInput = document.getElementById('fecha');
const cargarBtn = document.getElementById('cargarLista');
const modal = document.getElementById('modal');
const cerrarModal = document.getElementById('cerrarModal');
const formJustificacion = document.getElementById('formJustificacion');
const modalAlumno = document.getElementById('modalAlumno');
const motivoInput = document.getElementById('motivo');
const evidenciaInput = document.getElementById('evidencia');
const exportCsvBtn = document.getElementById('exportCsv');
const verReporteBtn = document.getElementById('verReporte');
const reporte = document.getElementById('reporte');
const contenidoReporte = document.getElementById('contenidoReporte');
const cerrarReporte = document.getElementById('cerrarReporte');

let fechaSeleccionada = null;
let asistenciaDelDia = {};
let editingAlumnoId = null;

fechaInput.valueAsDate = new Date();

function cargarLista(){
  fechaSeleccionada = fechaInput.value;
  const clave = `asistencia_${fechaSeleccionada}`;
  const guardado = localStorage.getItem(clave);
  if (guardado) {
    asistenciaDelDia = JSON.parse(guardado);
  } else {
    asistenciaDelDia = {};
    estudiantesEjemplo.forEach(est => {
      asistenciaDelDia[est.id] = { estado: 'presente', tipo_tardanza: null, justificacion: null };
    });
  }
  renderTabla();
}

function guardarLocal(){
  const clave = `asistencia_${fechaSeleccionada}`;
  localStorage.setItem(clave, JSON.stringify(asistenciaDelDia));
}

function renderTabla(){
  tablaBody.innerHTML = '';
  estudiantesEjemplo.forEach(est => {
    const row = document.createElement('tr');
    const state = asistenciaDelDia[est.id] || { estado: 'presente', tipo_tardanza: null };

    row.innerHTML = `
      <td>${est.nombre}</td>
      <td>${state.estado === 'presente' ? 'Presente' : state.estado === 'ausente' ? 'Ausente' : 'Tarde'}</td>
      <td>${state.estado === 'tarde' ? (state.tipo_tardanza ? state.tipo_tardanza : '') : ''}</td>
      <td class="actions">
        <button class="status-btn status-presente" data-id="${est.id}" data-estado="presente">Presente</button>
        <button class="status-btn status-ausente" data-id="${est.id}" data-estado="ausente">Ausente</button>
        <button class="status-btn status-tarde" data-id="${est.id}" data-estado="tarde">Tarde</button>
        <button class="status-btn" data-id="${est.id}" data-action="justificar">Justificar</button>
      </td>
    `;

    row.querySelectorAll('button').forEach(btn => {
      btn.addEventListener('click', () => {
        const id = Number(btn.dataset.id);
        if (btn.dataset.action === 'justificar'){
          abrirModalJustificacion(id);
          return;
        }
        const nuevoEstado = btn.dataset.estado;
        if (!fechaSeleccionada){
          alert('Seleccione una fecha y presione "Cargar lista"');
          return;
        }
        if (nuevoEstado === 'tarde'){
          const tipo = prompt('Marcar tipo de tardanza: escriba R (retardo) o OK (justificado)');
          asistenciaDelDia[id] = { estado: 'tarde', tipo_tardanza: tipo ? tipo.toUpperCase() : null, justificacion: null };
        } else if (nuevoEstado === 'presente'){
          asistenciaDelDia[id] = { estado: 'presente', tipo_tardanza: null, justificacion: null };
        } else {
          asistenciaDelDia[id] = { estado: 'ausente', tipo_tardanza: null, justificacion: null };
        }
        guardarLocal();
        renderTabla();
      });
    });

    tablaBody.appendChild(row);
  });
}

function abrirModalJustificacion(id){
  editingAlumnoId = id;
  const est = estudiantesEjemplo.find(e => e.id === id);
  modalAlumno.textContent = `Alumno: ${est.nombre} — Fecha: ${fechaSeleccionada}`;
  motivoInput.value = '';
  evidenciaInput.value = '';
  modal.classList.remove('hidden');
}

cerrarModal.addEventListener('click', () => {
  modal.classList.add('hidden');
});

formJustificacion.addEventListener('submit', (e) => {
  e.preventDefault();
  const motivo = motivoInput.value.trim();
  const file = evidenciaInput.files[0];

  const justObj = { motivo, evidenciaNombre: file ? file.name : null, fecha_registro: new Date().toISOString() };
  if (!fechaSeleccionada){
    alert('Seleccione una fecha y presione "Cargar lista"');
    return;
  }
  asistenciaDelDia[editingAlumnoId] = { estado: 'tarde', tipo_tardanza: 'OK', justificacion: justObj };
  guardarLocal();
  modal.classList.add('hidden');
  renderTabla();
});

exportCsvBtn.addEventListener('click', () => {
  if (!fechaSeleccionada){ alert('Cargue primero la lista de la fecha.'); return; }
  const rows = [['Estudiante','Fecha','Estado','TipoTardanza','Justificacion','Evidencia']];
  estudiantesEjemplo.forEach(est => {
    const a = asistenciaDelDia[est.id] || { estado: 'presente' };
    const just = a.justificacion ? a.justificacion.motivo : '';
    const evid = a.justificacion ? a.justificacion.evidenciaNombre : '';
    rows.push([est.nombre, fechaSeleccionada, a.estado, a.tipo_tardanza || '', just, evid]);
  });
  const csvContent = rows.map(r => r.map(c => `"${String(c).replace(/"/g,'""')}"`).join(',')).join('\\n');
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = `asistencia_${fechaSeleccionada}.csv`; a.click();
  URL.revokeObjectURL(url);
});

verReporteBtn.addEventListener('click', () => {
  const dt = new Date(fechaInput.value);
  const mes = dt.getMonth();
  const anio = dt.getFullYear();
  const keys = Object.keys(localStorage).filter(k => k.startsWith('asistencia_'));
  const registros = [];
  keys.forEach(k => {
    const fecha = k.replace('asistencia_','');
    const f = new Date(fecha);
    if (f.getMonth() === mes && f.getFullYear() === anio){
      const data = JSON.parse(localStorage.getItem(k));
      registros.push({ fecha, data });
    }
  });

  const resumen = estudiantesEjemplo.map(est => {
    let totalTarde = 0, just = 0, noJust = 0, totalDias = registros.length;
    registros.forEach(r => {
      const a = r.data[est.id];
      if (!a) return;
      if (a.estado === 'tarde'){
        totalTarde++;
        if (a.justificacion) just++; else noJust++;
      }
    });
    return { nombre: est.nombre, totalTarde, just, noJust, totalDias };
  });

  contenidoReporte.innerHTML = '<table style=\"width:100%;\"><tr><th>Estudiante</th><th>Tardanzas</th><th>Justificadas</th><th>No justificadas</th><th>Días registrados</th></tr>' +
    resumen.map(r => `<tr><td>${r.nombre}</td><td>${r.totalTarde}</td><td>${r.just}</td><td>${r.noJust}</td><td>${r.totalDias}</td></tr>`).join('') + '</table>';
  reporte.classList.remove('hidden');
});

cerrarReporte.addEventListener('click', () => { reporte.classList.add('hidden'); });

cargarBtn.addEventListener('click', cargarLista);
document.addEventListener('DOMContentLoaded', cargarLista);
