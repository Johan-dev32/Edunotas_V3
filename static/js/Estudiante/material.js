// Datos simulados - en un sistema real vendrían del servidor
const materials = JSON.parse(document.getElementById("materials-data").textContent).map(m => ({
    id: m.id,
    title: m.titulo,
    description: m.descripcion || "",
    type: m.tipo.toLowerCase(),
    course: "Curso", // Luego puedes reemplazar con el nombre real
    usage: "Material del curso",
    files: [
        {
            label: m.tipo,
            url: m.url

        }
    ]
}));

// Init
const materialsList = document.getElementById('materials-list');
const searchInput = document.getElementById('search');
const filterType = document.getElementById('filter-type');
const filterCourse = document.getElementById('filter-course');
const clearBtn = document.getElementById('clear-filters');

// ⭐ ELIMINAMOS todo lo del modal porque ya NO se usa


function populateCourseFilter(){
  const courses = Array.from(new Set(materials.map(m => m.course)));
  courses.forEach(c => {
    const opt = document.createElement('option');
    opt.value = c; 
    opt.textContent = c;
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
        <button class="primary" data-id="${m.id}">Abrir recurso</button>
      </div>
    `;

    const openBtn = card.querySelector('.primary');
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


function openResource(m){
  // Abre PDF, enlaces, imágenes, lo que sea
  if(m.files && m.files.length > 0 && m.files[0].url !== '#'){
    window.open(m.files[0].url, '_blank', 'noopener');
  } else {
    alert('Recurso no disponible.');
  }
}


function applyFilters(){
  const q = searchInput.value.trim().toLowerCase();
  const type = filterType.value;
  const course = filterCourse.value;

  const results = materials.filter(m => {
    const matchesQ = q === '' || 
      [m.title, m.description, m.course].join(' ').toLowerCase().includes(q);

    const matchesType = type === 'all' || m.type === type;
    const matchesCourse = course === 'all' || m.course === course;

    return matchesQ && matchesType && matchesCourse;
  });

  renderMaterials(results);
}

searchInput.addEventListener('input', applyFilters);
filterType.addEventListener('change', applyFilters);
filterCourse.addEventListener('change', applyFilters);

clearBtn.addEventListener('click', () => {
  searchInput.value = '';
  filterType.value = 'all';
  filterCourse.value = 'all';
  applyFilters();
});


// Helpers
function truncate(str, n){ 
  return (str.length > n) ? str.slice(0, n - 1) + '…' : str; 
}

function escapeHtml(unsafe){
  return unsafe.replace(/[&<"'`=/]/g, function(s){ 
    return ({
      '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;',
      "'":'&#39;', '/':'&#x2F;', '=':'&#x3D;', '`':'&#x60;'
    })[s]; 
  });
}


// Start
populateCourseFilter();
renderMaterials(materials);
