document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('justification-modal');
    const closeBtn = document.querySelector('.close-btn');
    const justificationForm = document.getElementById('justification-form');
    const faltaIdInput = document.getElementById('falta-id-input');

    // 1. Abrir Modal al hacer clic en "Justificar"
    document.querySelectorAll('.justify-btn').forEach(button => {
        button.addEventListener('click', (e) => {
            const faltaId = e.target.dataset.id;
            faltaIdInput.value = faltaId; // Guardar el ID de la falta
            modal.style.display = 'block';
        });
    });

    // 2. Cerrar Modal con el botón 'x' o haciendo clic fuera
    closeBtn.addEventListener('click', () => {
        modal.style.display = 'none';
    });

    window.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    });

    // 3. Manejar el envío del formulario
    justificationForm.addEventListener('submit', (e) => {
        e.preventDefault();
        
        // **IMPORTANTE: Aquí es donde conectas con el servidor (backend)**
        const formData = new FormData(justificationForm);
        
        // Crear un objeto con los datos para enviar
        const dataToSend = {
            falta_id: formData.get('faltaId'),
            motivo: formData.get('reason'),
            detalles: formData.get('details'),
            // El archivo adjunto debe manejarse de forma diferente en el backend
            // formData ya lo incluye, pero el ejemplo de fetch es más simple con JSON
        };

        // Simulación del envío (deberás reemplazar esto con una llamada real a tu API)
        fetch('/api/justificar-falta', { 
            method: 'POST',
            body: formData // Usar formData para enviar el archivo
            // Headers se omiten al usar formData, el navegador los maneja
        })
        .then(response => {
            if (response.ok) {
                return response.json();
            }
            throw new Error('Error al justificar la falta');
        })
        .then(result => {
            alert('¡Justificación enviada con éxito! Esperando revisión.');
            modal.style.display = 'none';
            // Opcional: Recargar la tabla o quitar la fila de la falta justificada
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Hubo un problema al enviar la justificación.');
        });
    });
});