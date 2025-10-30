// --- Datos iniciales ---
const SAMPLE = [
  {id:1,title:'Clase 1 - Introducción a funciones',course:'Matemáticas ',type:'explicacion',desc:'Presentación y ejemplos básicos',link:'https://example.com/presentacion.pdf'},
  {id:2,title:'Tarea semana 2',course:'Biología ',type:'tarea',desc:'Preguntas sobre cap. 3',link:'https://drive.google.com/file/d/xxx'},
  {id:3,title:'Podcast: Historia breve',course:'Historia ',type:'lectura',desc:'Episodio sobre la independencia',link:'audio:https://podcasts.example/ep1.mp3'},
  {id:4,title:'Video: Experimento 5',course:'Química ',type:'refuerzo',desc:'Demostración en laboratorio',link:'https://youtube.com/watch?v=videoid'}
];

// --- Claves y acceso al DOM ---
const KEY = 'materiales_v1';
const grid = document.getElementById('grid');
const count = document.getElementById('count');
const empty = document.getElementById('empty');
const searchInput = document.getElementById('searchInput');
const filterType = document.getElementById('filterType');
const courseFilter = document.getElementById('courseFilter');
const coursesList = document.getElementById('coursesList');

// modales
const modal = document.getElementById('modal');
const openUpload = document.getElementById('openUpload');
const closeModal = document.getElementById('closeModal');
const saveMaterial = document.getElementById('saveMaterial');

const detailModal = document.getElementById('detailModal');
const dClose = document.getElementById('dClose');
const dDownload = document.getElementById('dDownload');

// --- Métodos de almacenamiento ---
function loadMaterials(){
  const raw = localStorage.getItem(KEY);
  if(!raw){
    localStorage.setItem(KEY, JSON.stringify(SAMPLE));
    return SAMPLE;
  }
  try { return JSON.parse(raw); }
  catch(e){ localStorage.setItem(KEY, JSON.stringify(SAMPLE)); return SAMPLE; }
}

function saveMaterials(list){ localStorage.setItem(KEY, JSON.stringify(list)); }

// --- Renderizado principal ---
function render(){
  const all = loadMaterials();
  const q = searchInput.value.trim().toLowerCase();
  const type = filterType.value;
  const course = courseFilter.value;

  let filtered = all.filter(m => {
    if(type !== 'all' && m.type !== type) return false;
    if(course !== 'all' && m.course !== course) return false;
    if(!q) return true;
    return (m.title + m.desc + m.course).toLowerCase().includes(q);
  });

  grid.innerHTML = '';
  empty.style.display = filtered.length === 0 ? 'block' : 'none';
  count.textContent = filtered.length;

  const courses = Array.from(new Set(all.map(x => x.course))).sort();
  coursesList.innerHTML = courses.map(c => `<div>${c}</div>`).join('');
  courseFilter.innerHTML = '<option value="all">Todos los cursos</option>' + courses.map(c => `<option value="${escapeHtml(c)}">${escapeHtml(c)}</option>`).join('');

  filtered.forEach(m => {
    const card = document.createElement('article');
    card.className = 'card';
    card.innerHTML = `
      <div style="display:flex;justify-content:space-between;align-items:center">
        <div>
          <div class="meta">${escapeHtml(m.course)}</div>
          <div class="title">${escapeHtml(m.title)}</div>
        </div>
        <div class="badges"><div class="badge">${typeLabel(m.type)}</div></div>
      </div>
      <div class="small">${escapeHtml(m.desc)}</div>
      <footer>
        <div class="small">${new Date().toLocaleDateString()}</div>
        <button class="openBtn" data-id="${m.id}">Ver</button>
      </footer>`;
    grid.appendChild(card);
  });

  document.querySelectorAll('.openBtn').forEach(b => b.addEventListener('click', e => {
    openDetail(Number(e.currentTarget.dataset.id));
  }));
}

// --- Helpers ---
function escapeHtml(str){ return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
function typeLabel(t){ return {explicacion:'Explicación',tarea:'Tarea',refuerzo:'Refuerzo',lectura:'Lectura'}[t] || t; }

// --- Detalle de material ---
function openDetail(id){
  const all = loadMaterials();
  const m = all.find(x => x.id === id);
  if(!m) return;

  document.getElementById('dTitle').textContent = m.title;
  document.getElementById('dMeta').textContent = `${m.course} • ${typeLabel(m.type)}`;
  document.getElementById('dDesc').textContent = m.desc;
  const dContent = document.getElementById('dContent');
  dContent.innerHTML = '';

  if(m.link){
    if(m.link.startsWith('audio:')){
      const src = m.link.replace('audio:','');
      dContent.innerHTML = `<audio controls src="${escapeHtml(src)}"></audio>`;
      dDownload.onclick = () => window.open(src,'_blank');
    } else if(m.link.includes('youtube')||m.link.includes('youtu.be')){
      const url = new URL(m.link);
      let vid = url.searchParams.get('v') || m.link.split('v=')[1] || m.link.split('/').pop();
      dContent.innerHTML = `<div style="position:relative;padding-top:56%"><iframe src="https://www.youtube.com/embed/${escapeHtml(vid)}" style="position:absolute;inset:0;width:100%;height:100%;border:0" allowfullscreen></iframe></div>`;
      dDownload.onclick = () => window.open(m.link,'_blank');
    } else {
      dContent.innerHTML = `<div class='small'>Enlace / archivo: <a href='#' id='dLink'>Abrir</a></div>`;
      document.getElementById('dLink').addEventListener('click', e => { e.preventDefault(); window.open(m.link,'_blank'); });
      dDownload.onclick = () => window.open(m.link,'_blank');
    }
  }

  detailModal.classList.add('show');
}

// --- Subir material ---
openUpload.addEventListener('click', () => modal.classList.add('show'));
closeModal.addEventListener('click', () => modal.classList.remove('show'));
dClose.addEventListener('click', () => detailModal.classList.remove('show'));

saveMaterial.addEventListener('click', () => {
  const title = document.getElementById('mTitle').value.trim();
  const course = document.getElementById('mCourse').value.trim() || 'Sin curso';
  const type = document.getElementById('mType').value;
  const desc = document.getElementById('mDesc').value.trim();
  const link = document.getElementById('mLink').value.trim();

  if(!title){ alert('El título es obligatorio'); return; }

  const all = loadMaterials();
  const id = all.reduce((a,b) => Math.max(a,b.id), 0) + 1;
  all.push({id,title,course,type,desc,link});
  saveMaterials(all);
  modal.classList.remove('show');

  document.getElementById('mTitle').value = '';
  document.getElementById('mCourse').value = '';
  document.getElementById('mDesc').value = '';
  document.getElementById('mLink').value = '';
  render();
});

[searchInput, filterType, courseFilter].forEach(el => el.addEventListener('input', render));

render();
document.addEventListener('keydown', e => { if(e.key === 'Escape'){ modal.classList.remove('show'); detailModal.classList.remove('show'); } });
