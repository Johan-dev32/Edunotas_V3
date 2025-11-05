
const currentUser = { id: 'u1', name: 'Prof. Juan Pérez', role: 'docente' }; 
const students = [
  { id: 's1', name: 'Ana Gómez' },
  { id: 's2', name: 'Carlos Ruiz' },
  { id: 's3', name: 'María López' }
];


let citas = [];
let editingCitaId = null;

const currentUserEl = document.getElementById('currentUser');
const studentSelect = document.getElementById('studentSelect');
const form = document.getElementById('formCita');
const tablaBody = document.querySelector('#tablaCitas tbody');
const filtroEstado = document.getElementById('filtroEstado');
const buscar = document.getElementById('buscar');
const modal = document.getElementById('modalObserv');
const formObserv = document.getElementById('formObserv');
const observacionesInput = document.getElementById('observaciones');
const cerrarModalBtn = document.getElementById('cerrarModal');
let citaSeleccionadaParaAtender = null;

function init() {
  if (!studentSelect) {
    console.error("No se encontró el select de estudiantes");
    return;
  }
  currentUserEl.textContent = currentUser.name + ' (' + currentUser.role + ')';
  students.forEach(s => {
    const opt = document.createElement('option');
    opt.value = s.id;
    opt.textContent = s.name;
    studentSelect.appendChild(opt);
  });
  renderTabla();
}



function formatDate(d){return d}
function generarId(prefix='c'){return prefix + Math.random().toString(36).slice(2,9)}
function findStudentName(id){const s=students.find(x=>x.id===id); return s? s.name : 'Desconocido'}

function tieneConflicto(fecha, hora){
  return citas.some(c => c.fecha===fecha && c.hora===hora);
}

function perteneceAlumnoAlDocente(studentId){
  return students.some(s => s.id === studentId);
}


function renderTabla(){
  tablaBody.innerHTML = '';
  const q = buscar.value.toLowerCase();
  const estadoFiltro = filtroEstado.value;
  const rows = citas.filter(c => {
    if(estadoFiltro!=='all' && c.estado!==estadoFiltro) return false;
    if(q && !(findStudentName(c.studentId).toLowerCase().includes(q) || c.motivo.toLowerCase().includes(q))) return false;
    return true;
  });

  rows.forEach(c => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${findStudentName(c.studentId)}</td>
      <td>${c.motivo}</td>
      <td>${formatDate(c.fecha)}</td>
      <td>${c.hora}</td>
      <td><span class="status ${c.estado}">${c.estado}</span>
          <div style="font-size:11px;color:#666;margin-top:6px">R:${c.received? '✓':''} L:${c.read? '✓':''} C:${c.confirmed? '✓':''}</div>
      </td>
      <td class="actions">
        <button data-id="${c.id}" class="btnVer">Ver</button>
        ${ (['docente','coordinador','orientador','directivo'].includes(currentUser.role)) ? `<button data-id="${c.id}" class="btnAtender">Atender</button>` : '' }
        ${ (['docente','coordinador','orientador','directivo'].includes(currentUser.role)) ? `<button data-id="${c.id}" class="btnReprog">Reprogramar</button>` : '' }
      </td>
    `;
    tablaBody.appendChild(tr);
  });

  // attach events
  document.querySelectorAll('.btnVer').forEach(b => b.addEventListener('click', e=> mostrarDetalle(e.target.dataset.id)));
  document.querySelectorAll('.btnAtender').forEach(b => b.addEventListener('click', e=> abrirModalAtender(e.target.dataset.id)));
  document.querySelectorAll('.btnReprog').forEach(b=> b.addEventListener('click', e=> reprogramarCita(e.target.dataset.id)));
}

function mostrarDetalle(id){
  const c = citas.find(x=>x.id===id);
  if(!c) return alert('Citación no encontrada');
  alert(`Citación para ${findStudentName(c.studentId)}\nMotivo: ${c.motivo}\nFecha: ${c.fecha} ${c.hora}\nLugar: ${c.lugar}\nEstado: ${c.estado}\nObservaciones: ${c.observaciones || '---'}`);
}

// Crear citación
form.addEventListener('submit', e=>{
  e.preventDefault();
  if(!['docente','coordinador','orientador','directivo'].includes(currentUser.role)) return alert('No tienes permisos para crear citaciones');

  const studentId = studentSelect.value;
  const motivo = document.getElementById('motivo').value.trim();
  const fecha = document.getElementById('fecha').value;
  const hora = document.getElementById('hora').value;
  const lugar = document.getElementById('lugar').value.trim();
  const medio = document.getElementById('medio').value;
  const archivo = document.getElementById('adjunto').files[0];

  if(!studentId || !motivo || !fecha || !hora || !lugar) return alert('Completa todos los campos obligatorios');
  if(!perteneceAlumnoAlDocente(studentId)) return alert('El estudiante no está asociado a tu grupo');
  if(tieneConflicto(fecha,hora)) return alert('Ya existe una citación en esa fecha y hora (conflicto de horario)');

  const id = generarId();
  const nueva = { id, studentId, motivo, fecha, hora, lugar, quien: currentUser.name, medio, estado:'pendiente', received:false, read:false, confirmed:false, observaciones:'', attachments: [] };
  if(archivo) nueva.attachments.push({ name: archivo.name, size: archivo.size });

  citas.push(nueva);
  // simulación de envío
  if(medio==='email'){
    nueva.received = true; // asumimos entrega
    console.log('Envio por email a acudiente de', findStudentName(studentId));
  } else {
    nueva.received = true; // notificación plataforma
    console.log('Notificación en plataforma creada para', findStudentName(studentId));
  }

  renderTabla();
  form.reset();
  alert('Citación creada y enviada.');
});

// Reprogramar (simple, reabre formulario con nuevos datos)
function reprogramarCita(id){
  const c = citas.find(x=>x.id===id);
  if(!c) return;
  if(!confirm('¿Reprogramar la citación? Se abrirá un prompt para nueva fecha y hora.')) return;
  const nuevaFecha = prompt('Nueva fecha (YYYY-MM-DD):', c.fecha);
  const nuevaHora = prompt('Nueva hora (HH:MM):', c.hora);
  if(!nuevaFecha || !nuevaHora) return alert('Fecha u hora inválida');
  if(tieneConflicto(nuevaFecha, nuevaHora)) return alert('Conflicto con otra citación');
  c.fecha = nuevaFecha; c.hora = nuevaHora; c.estado = 'reprogramada';
  renderTabla();
}

// Atender -> abrir modal de observaciones (obligatorio antes de marcar atendida)
function abrirModalAtender(id){
  citaSeleccionadaParaAtender = id;
  observacionesInput.value = '';
  modal.classList.remove('hidden');
}

cerrarModalBtn.addEventListener('click', ()=>{ modal.classList.add('hidden'); citaSeleccionadaParaAtender = null; });

formObserv.addEventListener('submit', e=>{
  e.preventDefault();
  const texto = observacionesInput.value.trim();
  if(!texto) return alert('Debes registrar observaciones para marcar la citación como atendida');
  const c = citas.find(x=>x.id===citaSeleccionadaParaAtender);
  if(!c) return alert('Citación no encontrada');
  c.observaciones = texto;
  c.estado = 'atendida';
  renderTabla();
  modal.classList.add('hidden');
  citaSeleccionadaParaAtender = null;
  alert('Citación marcada como atendida y observaciones registradas.');
});

// Filtros
filtroEstado.addEventListener('change', renderTabla);
buscar.addEventListener('input', renderTabla);

document.addEventListener('DOMContentLoaded', () => {
  init();
});


