document.addEventListener('DOMContentLoaded', () => {
  const tableBody = document.querySelector('#tabla-repitentes tbody');
  const modalAgregarEl = document.getElementById('modalAgregar');
  const modalAgregar = new bootstrap.Modal(modalAgregarEl);
  const btnAbrirAgregar = document.getElementById('btnAbrirAgregar');
  const formAgregar = document.getElementById('formAgregar');

  // Abrir modal
  btnAbrirAgregar.addEventListener('click', () => modalAgregar.show());

  // Enviar formulario
  formAgregar.addEventListener('submit', async (e) => {
  e.preventDefault();
  const formData = new FormData(formAgregar);

  try {
    const res = await fetch('/administrador/repitentes/agregar', {
      method: 'POST',
      body: formData
    });

    const result = await res.json();

    if (res.ok && result.success) {
      // Mostrar alerta según si está matriculado o no
      if (result.matriculado) {
        Swal.fire({
          icon: 'info',
          title: '⚠️ Estudiante ya matriculado',
          text: 'Este estudiante ya está registrado en el sistema de matrículas.',
          confirmButtonColor: '#3085d6',
          confirmButtonText: 'Entendido'
        });
      } else {
        Swal.fire({
          icon: 'success',
          title: '✅ Registro exitoso',
          text: result.message,
          confirmButtonColor: '#28a745'
        });
      }

      // Actualizar tabla sin recargar
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${formData.get('tipo_documento')}</td>
        <td>${formData.get('numero_documento')}</td>
        <td>${formData.get('nombre')}</td>
        <td>${formData.get('curso')}</td>
      `;
      tableBody.appendChild(tr);
      formAgregar.reset();
      modalAgregar.hide();

    } else {
      Swal.fire({
        icon: 'error',
        title: '❌ Error',
        text: result.error || 'No se pudo registrar el estudiante.',
        confirmButtonColor: '#d33'
      });
    }

  } catch (err) {
    console.error(err);
    Swal.fire({
      icon: 'error',
      title: 'Error de conexión',
      text: 'No se pudo conectar con el servidor.',
      confirmButtonColor: '#d33'
    });
  }
});
});