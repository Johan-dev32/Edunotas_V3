
  // Obtener los parámetros de la URL
  const params = new URLSearchParams(window.location.search);
  const materia = params.get('materia');

  // Si hay una materia, cambiar el título
  if (materia) {
    const titulo = document.querySelector('.titulo');
    titulo.textContent = `TAREAS PENDIENTES DE ${materia.toUpperCase()}`;
  }

