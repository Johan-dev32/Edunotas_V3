document.addEventListener('DOMContentLoaded', function() {
    // Asegúrate de que los IDs coincidan con tu HTML
    const btnGuardar = document.getElementById('btnGuardar');
    const form = document.getElementById('form'); 

    // Define tus IDs de EmailJS aquí
    const serviceID = 'default_service'; // O el ID de tu servicio en EmailJS
    const templateID = 'template_mnpwosp'; // O el ID de tu plantilla en EmailJS

    if (!form) {
        console.error("Error: No se encontró el formulario con ID 'form'.");
        return;
    }

    form.addEventListener('submit', function(event) {
        event.preventDefault();

        // 1. Mostrar estado de carga inicial (Guardando en DB)
        Swal.fire({
            title: 'Guardando Citación...',
            text: 'Registrando datos en la base de datos.',
            icon: 'info',
            allowOutsideClick: false,
            showConfirmButton: false
        });

        // Crear FormData para enviar los datos a Flask (base de datos)
        const formData = new FormData(form);
        
        // Función para cambiar el texto del botón durante la operación
        btnGuardar.innerText = 'Enviando...'; 
        
        // 2. Primer paso: Enviar datos a la base de datos (Flask)
        fetch("/administrador/citacion/registro", { // <-- ¡Ruta corregida aquí!
            method: "POST",
            body: formData,
        })
        .then(response => response.json().then(data => ({ status: response.status, body: data })))
        .then(res => {
            if (res.status === 200 && res.body.success) {
                
                // 3. Si la DB fue exitosa, enviamos el correo con EmailJS
                Swal.update({
                    title: 'Guardado en DB. Enviando Correo...',
                    text: 'El registro fue exitoso. Procesando el envío del email.',
                });

                emailjs.sendForm(serviceID, templateID, form)
                    .then(() => {
                        // Éxito total: DB y Email
                        Swal.fire({
                            icon: 'success',
                            title: '¡Citación Enviada y Guardada!',
                            text: 'El correo ha sido enviado y el registro se guardó en la base de datos.',
                        });
                        form.reset(); 
                        btnGuardar.innerText = 'Enviar Citación';

                    }, (error) => {
                        // Error de EmailJS (pero DB ya está actualizada)
                        Swal.fire({
                            icon: 'warning',
                            title: '¡Guardado en DB, pero error al enviar Email!',
                            text: `Fallo al enviar correo: ${JSON.stringify(error)}`,
                        });
                        btnGuardar.innerText = 'Enviar Citación';
                    });

            } else {
                // Error al guardar en la DB (Flask devolvió un error)
                Swal.fire({
                    icon: 'error',
                    title: 'Error de Registro',
                    text: res.body.error || 'Fallo al guardar la citación en el servidor.',
                });
                btnGuardar.innerText = 'Enviar Citación';
            }
        })
        .catch((error) => {
            // Error de conexión (fetch falló)
            console.error("Error de conexión:", error);
            Swal.fire({
                icon: 'error',
                title: 'Error de Conexión',
                text: 'No se pudo conectar con el servidor para guardar la citación.',
            });
            btnGuardar.innerText = 'Enviar Citación';
        });
    });
});