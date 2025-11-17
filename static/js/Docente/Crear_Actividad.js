document.addEventListener('DOMContentLoaded', () => {
  const pdfUpload = document.getElementById('pdfUpload');
  const uploadBox = document.querySelector('.upload-box');
  const publicarBtn = document.querySelector('.btn-subir');
  const form = publicarBtn.closest('form');

  // Contenedor visible donde solo mostramos el nombre (NO borrar el input)
  let fileLabel = document.createElement('div');
  fileLabel.classList.add('mt-2', 'fw-semibold', 'text-center');
  uploadBox.appendChild(fileLabel);

  // === Mostrar nombre del PDF seleccionado ===
  pdfUpload.addEventListener('change', (event) => {
    const file = event.target.files[0];

    if (file) {
      fileLabel.textContent = `📄 ${file.name}`;
    } else {
      fileLabel.textContent = '';
    }
  });

  // === Modal de advertencia antes de enviar ===
  function mostrarAdvertencia(mensaje, onAceptar, onCancelar) {
    const modal = document.createElement('div');
    modal.classList.add('modal-advertencia');
    modal.innerHTML = `
      <div class="modal-contenido">
        <p class="mb-4 fw-semibold">${mensaje}</p>
        <div class="text-center">
          <button class="btn btn-success me-3" id="btnAceptar">Aceptar</button>
          <button class="btn btn-danger" id="btnCancelar">Cancelar</button>
        </div>
      </div>
    `;
    document.body.appendChild(modal);

    document.getElementById('btnAceptar').addEventListener('click', () => {
      modal.remove();
      onAceptar && onAceptar();
    });

    document.getElementById('btnCancelar').addEventListener('click', () => {
      modal.remove();
      onCancelar && onCancelar();
    });
  }

  // === Mostrar alerta flotante ===
  function mostrarMensaje(texto, tipo = 'danger') {
    const alerta = document.createElement('div');
    alerta.classList.add('alert', `alert-${tipo}`, 'position-fixed', 'bottom-0', 'end-0', 'm-4', 'shadow');
    alerta.textContent = texto;
    document.body.appendChild(alerta);
    setTimeout(() => alerta.remove(), 3500);
  }

  // === Validar formulario antes de publicar ===
  function validarFormulario() {
    const titulo = form.querySelector('input[name="titulo"]').value.trim();
    const instrucciones = form.querySelector('textarea[name="instrucciones"]').value.trim();
    const tipo = form.querySelector('select[name="tipo"]').value;
    const estado = form.querySelector('select[name="estado"]').value;
    const porcentaje = parseFloat(form.querySelector('input[name="porcentaje"]').value);
    const fecha = form.querySelector('input[name="fecha"]').value;
    const hora = form.querySelector('input[name="hora"]').value;

    if (!titulo) return "El título es obligatorio.";
    if (!instrucciones) return "Las instrucciones son obligatorias.";
    if (!tipo) return "Debes seleccionar un tipo de actividad.";
    if (!estado) return "Selecciona un estado válido.";
    if (isNaN(porcentaje) || porcentaje <= 0 || porcentaje > 100)
      return "El porcentaje debe estar entre 1 y 100.";
    if (!fecha) return "Selecciona una fecha de entrega.";
    if (!hora) return "Selecciona una hora de entrega.";

    const hoy = new Date();
    const fechaSeleccionada = new Date(fecha);
    if (fechaSeleccionada < hoy.setHours(0, 0, 0, 0)) {
      return "La fecha debe ser futura o actual.";
    }

    return null;
  }

  // === Acción al hacer clic en PUBLICAR ===
  publicarBtn.addEventListener('click', (e) => {
    e.preventDefault(); // Evita envío automático del form

    const error = validarFormulario();
    if (error) {
      mostrarMensaje(`⚠️ ${error}`, 'warning');
      return;
    }

    mostrarAdvertencia(
      '¿Deseas publicar esta actividad?',
      () => { form.submit(); },
      () => mostrarMensaje('❌ Publicación cancelada', 'danger')
    );
  });
});
