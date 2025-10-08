document.addEventListener('DOMContentLoaded', () => {
  const pdfUpload = document.getElementById('pdfUpload');
  const uploadBox = document.querySelector('.upload-box');
  const publicarBtn = document.querySelector('.btn-subir');

  // === Mostrar nombre del PDF seleccionado ===
  pdfUpload.addEventListener('change', (event) => {
    const file = event.target.files[0];
    uploadBox.innerHTML = ''; // limpiar contenido

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

  // === Crear advertencia personalizada (modal simple con CSS) ===
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

    // Eventos
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
    mostrarAdvertencia(
      '¿Deseas publicar esta actividad?',
      () => mostrarMensaje('✅ Actividad publicada con éxito', 'success'),
      () => mostrarMensaje('❌ Publicación cancelada', 'danger')
    );
  });

  // === Mostrar mensaje final ===
  function mostrarMensaje(texto, tipo) {
    const alerta = document.createElement('div');
    alerta.classList.add('alert', `alert-${tipo}`, 'position-fixed', 'bottom-0', 'end-0', 'm-4', 'shadow');
    alerta.textContent = texto;
    document.body.appendChild(alerta);

    setTimeout(() => alerta.remove(), 3000);
  }
});
