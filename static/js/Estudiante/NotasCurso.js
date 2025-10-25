
  // Función para obtener parámetros de la URL
  function obtenerParametro(nombre) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(nombre);
  }

  // Cambiar el título según la materia
  document.addEventListener('DOMContentLoaded', () => {
    const materia = obtenerParametro('materia');
    if (materia) {
      // Cambia el texto del título principal
      document.querySelector('.titulo-principal').textContent = materia.toUpperCase();

      // También podrías actualizar la descripción si quieres
      document.querySelector('.descripcion').textContent = `Notas de la materia ${materia}`;
    }
  });

