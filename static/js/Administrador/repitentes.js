document.addEventListener('DOMContentLoaded', () => {
  const tableBody = document.querySelector('#tabla-repitentes tbody');
  const modalAgregarEl = document.getElementById('modalAgregar');
  const modalAgregar = new bootstrap.Modal(modalAgregarEl);
  const btnAbrirAgregar = document.getElementById('btnAbrirAgregar');
  const formAgregar = document.getElementById('formAgregar');

  btnAbrirAgregar.addEventListener('click', () => modalAgregar.show());

  formAgregar.addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(formAgregar);
    const payload = {
      tipo: formData.get('tipo_documento'),
      doc: formData.get('numero_documento'),
      nombre: formData.get('nombre'),
      curso: formData.get('curso')
    };

    try {
      const res = await fetch('/administrador/api/repitentes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const result = await res.json();

      if (res.ok && result.success) {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td>${result.tipo}</td>
          <td>${result.doc}</td>
          <td>${result.nombre}</td>
          <td>${result.veces}</td>
          <td>
            <button class="btn btn-sm btn-primary">
              <i class="bi bi-eye"></i> Ver
            </button>
          </td>
        `;
        tableBody.appendChild(tr);
        formAgregar.reset();
        modalAgregar.hide();
      } else {
        alert("⚠️ Error: " + (result.error || 'No se pudo registrar'));
      }
    } catch (err) {
      console.error(err);
      alert("❌ Error de conexión con el servidor");
    }
  });
});