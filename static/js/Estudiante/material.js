// Datos simulados - en un sistema real vendrían del servidor
const materials = [
  {
    id:1,
    title:'Introducción a Álgebra - Guía de estudio',
    description:'Documento con los conceptos básicos y ejercicios propuestos.',
    course:'Matemáticas I',
    type:'documento', // documento | enlace | video
    usage:'Lectura complementaria',
    files:[{label:'PDF - Guía', url:'#'}]
  },
  {
    id:2,
    title:'Video: Técnicas de resolución de problemas',
    description:'Video grabado por el docente con ejemplos resueltos en exámenes.',
    course:'Matemáticas I',
    type:'video',
    usage:'Explicación en clase',
    files:[{label:'YouTube', url:'https://www.youtube.com/'}]
  },
  {
    id:3,
    title:'Enlace interactivo - Juegos de vocabulario',
    description:'Plataforma recomendada para reforzar vocabulario.',
    course:'Lengua y Literatura',
    type:'enlace',
    usage:'Actividad de refuerzo',
    files:[{label:'Sitio', url:'https://example.com'}]
  }
];

// Init
const materialsList = document.getElementById('materials-list');
const searchInput = document.getElementById('search');
const filterType = document.getElementById('filter-type');
const filterCourse = document.getElementById('filter-course');
const clearBtn = document.getElementById('clear-filters');
const modal = document.getElementById('detailModal');
const modalTitle = document.getElementById('modal-title');
const modalDesc = document.getElementById('modal-desc');
const modalCourse = document.getElementById('modal-course');
const modalUsage = document.getElementById('modal-usage');
const modalLinks = document.getElementById('modal-links');
const closeModal = document.getElementById('closeModal');

function populateCourseFilter(){
  const courses = Array.from(new Set(materials.map(m => m.course)));
  courses.forEach(c => {
    const opt = document.createElement('option');
    opt.value = c; opt.textContent = c;
    filterCourse.appendChild(opt);
  });
}

function renderMaterials(list){
  materialsList.innerHTML = '';
  if(list.length === 0){
    materialsList.innerHTML = '<div class="card">No se encontraron materiales.</div>';
    return;
  }

  list.forEach(m => {
    const card = document.createElement('article');
    card.className = 'card';
    card.innerHTML = `
      <h4>${escapeHtml(m.title)}</h4>
      <p class="meta">${escapeHtml(m.course)} • ${typeLabel(m.type)}</p>
      <p>${truncate(escapeHtml(m.description),120)}</p>
      <div class="actions">
        <button class="btn view" data-id="${m.id}">Ver detalle</button>
        <button class="primary" data-id="${m.id}">Abrir recurso</button>
      </div>
    `;

    const viewBtn = card.querySelector('.view');
    const openBtn = card.querySelector('.primary');

    viewBtn.addEventListener('click', () => openModal(m.id));
    openBtn.addEventListener('click', () => openResource(m));

    materialsList.appendChild(card);
  });
}

function typeLabel(t){
  if(t==='documento') return 'Documento';
  if(t==='video') return 'Video/Podcast';
  if(t==='enlace') return 'Enlace externo';
  return t;
}

function openModal(id){
  const m = materials.find(x => x.id === Number(id));
  if(!m) return;
  modalTitle.textContent = m.title;
  modalCourse.textContent = `${m.course}`;
  modalDesc.textContent = m.description;
  modalUsage.textContent = m.usage;
  modalLinks.innerHTML = '';
  m.files.forEach(f => {
    const a = document.createElement('a');
    a.href = f.url;
    a.target = '_blank';
    a.rel = 'noopener noreferrer';
    a.textContent = f.label;
    a.className = 'btn';
    modalLinks.appendChild(a);
  });
  modal.showModal();
}

function openResource(m){
  // En el caso real, abriría el archivo o enlace. Aquí usamos la primera URL si existe.
  if(m.files && m.files.length>0 && m.files[0].url !== '#'){
    window.open(m.files[0].url, '_blank', 'noopener');
  } else {
    alert('Recurso no disponible para abrir (simulación).');
  }
}

closeModal.addEventListener('click', () => modal.close());
modal.addEventListener('cancel', (e) => e.preventDefault());

function applyFilters(){
  const q = searchInput.value.trim().toLowerCase();
  const type = filterType.value;
  const course = filterCourse.value;
  const results = materials.filter(m => {
    const matchesQ = q === '' || [m.title,m.description,m.course].join(' ').toLowerCase().includes(q);
    const matchesType = type === 'all' || m.type === type;
    const matchesCourse = course === 'all' || m.course === course;
    return matchesQ && matchesType && matchesCourse;
  });
  renderMaterials(results);
}
searchInput.addEventListener('input', applyFilters);
filterType.addEventListener('change', applyFilters);
filterCourse.addEventListener('change', applyFilters);
clearBtn.addEventListener('click', () => {searchInput.value=''; filterType.value='all'; filterCourse.value='all'; applyFilters();});

// Helpers
function truncate(str, n){ return (str.length>n)? str.slice(0,n-1)+'…' : str; }
function escapeHtml(unsafe){ return unsafe.replace(/[&<"'`=/]/g, function(s){ return ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;','/':'&#x2F;','=':'&#x3D;','`':'&#x60;'})[s]; }); }

// Start
populateCourseFilter();
renderMaterials(materials);

