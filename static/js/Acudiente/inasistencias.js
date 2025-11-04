const form = document.getElementById('justificacionForm');
const notifContainer = document.getElementById('notifications');
const formMessage = document.getElementById('formMessage');
const clearBtn = document.getElementById('clearBtn');

// Recuperar notificaciones guardadas en localStorage
const STORAGE_KEY = 'justificaciones_acudiente';
function loadStored(){
  try{
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw? JSON.parse(raw): [];
  }catch(e){
    console.error(e);
    return [];
  }
}

function store(entry){
  const arr = loadStored();
  arr.unshift(entry);
  localStorage.setItem(STORAGE_KEY, JSON.stringify(arr));
}

function renderNotifications(){
  const arr = loadStored();
  notifContainer.innerHTML = '';
  if(arr.length === 0){
    notifContainer.innerHTML = '<p class="empty">Aquí verás la notificación enviada al docente o coordinación.</p>';
    return;
  }
  arr.forEach(item => {
    const div = document.createElement('div');
    div.className = 'notif';
    const date = new Date(item.sentAt).toLocaleString();
    div.innerHTML = `<strong>${item.studentName}</strong> — <span style="color:var(--muted)">${date}</span>
                     <div style="margin-top:6px">${escapeHtml(item.reason)}</div>
                     <div style="margin-top:6px;font-size:0.85rem;color:var(--muted)">Enviado por: ${escapeHtml(item.relation)}</div>`;
    notifContainer.appendChild(div);
  });
}

function escapeHtml(text){
  if(!text) return '';
  return text.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

form.addEventListener('submit', (e)=>{
  e.preventDefault();
  const studentName = form.studentName.value.trim();
  const relation = form.relation.value.trim();
  const date = form.date.value;
  const reason = form.reason.value.trim();
  // Validación básica
  if(!studentName || !relation || !date || !reason){
    formMessage.textContent = 'Por favor completa todos los campos obligatorios.';
    formMessage.style.color = 'var(--danger)';
    return;
  }

  const entry = {
    studentName,
    relation,
    date,
    reason,
    // evidencia no se sube a servidor en este ejemplo; guardamos solo el nombre del archivo si existe
    evidenceName: form.evidence.files[0]?.name || null,
    sentAt: new Date().toISOString()
  };

  // Simular envío — guardar localmente y mostrar notificación
  store(entry);
  renderNotifications();

  // Mensaje al acudiente
  formMessage.textContent = 'Justificación enviada correctamente. El docente o coordinación fue notificado.';
  formMessage.style.color = 'green';

  // Opcional: limpiar campos
  form.reset();
});

clearBtn.addEventListener('click', ()=>{
  form.reset();
  formMessage.textContent = '';
});

// Inicializar
renderNotifications();

