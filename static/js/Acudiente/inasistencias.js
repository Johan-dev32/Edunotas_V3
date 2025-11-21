document.addEventListener('DOMContentLoaded', () => {
  // Modal Bootstrap actual para excusas
  const modal = document.getElementById('modalExcusa');
  if (!modal) return;

  modal.addEventListener('show.bs.modal', event => {
    const button = event.relatedTarget;
    if (!button) return;

    const faltaId = button.getAttribute('data-id') || '';
    const fecha = button.getAttribute('data-fecha') || '';
    const materia = button.getAttribute('data-materia') || '';

    const idInput = modal.querySelector('#excusaFaltaId');
    const fechaSpan = modal.querySelector('#excusaFecha');
    const materiaSpan = modal.querySelector('#excusaMateria');
    const form = modal.querySelector('form');

    if (idInput) idInput.value = faltaId;
    if (fechaSpan) fechaSpan.textContent = fecha;
    if (materiaSpan) materiaSpan.textContent = materia;
    if (form && faltaId) {
      form.action = `/acudiente/enviar_excusa/${faltaId}`;
    }
  });

  // No interceptamos el submit: el formulario se envía normal al backend
});