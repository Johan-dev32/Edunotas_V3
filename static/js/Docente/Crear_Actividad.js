document.addEventListener('DOMContentLoaded', () => {
  const pdfUpload = document.getElementById('pdfUpload');
  const uploadBox = document.querySelector('.upload-box');
  const publicarBtn = document.querySelector('.btn-subir');

  // === Mostrar nombre del PDF seleccionado ===
  pdfUpload.addEventListener('change', (event) => {
    const file = event.target.files[0];
    uploadBox.innerHTML = '';

    if (file) {
      const fileName = document.createElement('p');
      fileName.classList.add('fw-semibold', 'mt-2');
      fileName.textContent = `📄 ${file.name}`;
      uploadBox.appendChild(fileName);
    } else {
      uploadBox.innerHTML = `
        <label for="pdfUpload" class="d-block cursor-pointer">
          <i class="bi bi-file-earmark-pdf-fill fs-1 text-danger"></i>
          <p class="mt-2 fw-semibold">Adjuntar material en PDF</p>
        </label>
      `;
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

  // === Al hacer clic en PUBLICAR ACTIVIDAD ===
  publicarBtn.addEventListener('click', () => {
    const form = publicarBtn.closest('form'); // seleccionamos el formulario
    mostrarAdvertencia(
      '¿Deseas publicar esta actividad?',
      () => form.submit(), // si acepta, se envía el formulario
      () => mostrarMensaje('❌ Publicación cancelada', 'danger')
    );
  });

  function mostrarMensaje(texto, tipo) {
    const alerta = document.createElement('div');
    alerta.classList.add('alert', `alert-${tipo}`, 'position-fixed', 'bottom-0', 'end-0', 'm-4', 'shadow');
    alerta.textContent = texto;
    document.body.appendChild(alerta);
    setTimeout(() => alerta.remove(), 3000);
  }
});
