document.addEventListener("DOMContentLoaded", () => {
    const encuestasList = document.getElementById("encuestasList");
    const searchInput = document.getElementById("searchInput");
    const noEncuestasMessage = document.getElementById("noEncuestasMessage");

    
    function getEncuestas() {
        let encuestas = JSON.parse(localStorage.getItem("encuestas")) || [];
        return encuestas.map((encuesta) => ({
            ...encuesta,
            tiene_respuestas: false 
        }));
    }


    function renderEncuestas(encuestas) {
        encuestasList.innerHTML = ''; 

        if (encuestas.length === 0) {
            noEncuestasMessage.classList.remove('d-none');
        } else {
            noEncuestasMessage.classList.add('d-none');
        }

        encuestas.forEach(encuesta => {

            const puedeActuar = !encuesta.tiene_respuestas;
            const cardClass = puedeActuar ? 'border-primary' : 'border-danger';
            const tooltipTitle = puedeActuar 
                ? 'Editar o Eliminar esta encuesta' 
                : 'Esta encuesta tiene respuestas, no puede ser modificada.';
            
            const itemHTML = `
                <div class="p-3 border rounded shadow-sm d-flex align-items-center justify-content-between ${cardClass}">
                    <h5 class="mb-0 fw-bold">${encuesta.titulo}</h5>
                    
                    <div class="d-flex gap-2" title="${tooltipTitle}" data-bs-toggle="tooltip">
                        
                        <!-- BOTÓN DE EDITAR (Lápiz) -->
                        <button 
                            class="btn ${puedeActuar ? 'btn-outline-warning' : 'btn-outline-secondary'}" 
                            data-action="editar"
                            data-id="${encuesta.id}"
                            ${!puedeActuar ? 'disabled' : ''}
                        >
                            <i class="bi bi-pencil-square"></i> 
                        </button>

                        <!-- BOTÓN DE ELIMINAR (Basura) -->
                        <button 
                            class="btn ${puedeActuar ? 'btn-outline-danger' : 'btn-outline-secondary'}"
                            data-action="eliminar"
                            data-id="${encuesta.id}"
                            ${!puedeActuar ? 'disabled' : ''}
                        >
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </div>
            `;
            encuestasList.insertAdjacentHTML('beforeend', itemHTML);
        });


        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
        tooltipTriggerList.map(function (tooltipTriggerEl) {
          return new bootstrap.Tooltip(tooltipTriggerEl)
        })


        encuestasList.querySelectorAll('button').forEach(button => {
            if (!button.disabled) {

                button.addEventListener('click', handleAction);
            }
        });
    }


    searchInput.addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase();
        const allEncuestas = getEncuestas();
        const filteredEncuestas = allEncuestas.filter(encuesta => 
            encuesta.titulo.toLowerCase().includes(query)
        );
        renderEncuestas(filteredEncuestas);
    });


    function handleAction(e) {

        e.preventDefault(); 
        
        const id = e.currentTarget.dataset.id; 
        const action = e.currentTarget.dataset.action;

        console.log(`DEBUG: Acción disparada: ${action} para ID: ${id}`); 

        if (action === 'editar') {
            

            if (typeof CREAR_ENCUESTA_URL === 'undefined') {
                 console.error("ERROR: La variable CREAR_ENCUESTA_URL no está definida. Revisa la consola en la pestaña 'Network' y el código HTML.");
                 Swal.fire('Error', 'No se pudo obtener la URL de edición (CREAR_ENCUESTA_URL no definida).', 'error');
                 return;
            }

            const targetUrl = `${CREAR_ENCUESTA_URL}?id=${id}`;
            console.log("DEBUG: Redirigiendo a:", targetUrl); 
            window.location.href = targetUrl;
            
        } else if (action === 'eliminar') {
            confirmarEliminar(id);
        }
    }

    function confirmarEliminar(id) {
        Swal.fire({
            title: '¿Estás seguro?',
            text: "¡No podrás revertir la eliminación de la encuesta!",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#d33',
            cancelButtonColor: '#3085d6',
            confirmButtonText: 'Sí, ¡Eliminar!',
            cancelButtonText: 'Cancelar'
        }).then((result) => {
            if (result.isConfirmed) {
                eliminarEncuesta(id);
            }
        });
    }


    function eliminarEncuesta(id) {
        let encuestas = getEncuestas().filter(e => e.id != id); 
        

        const encuestasSinRespuestas = encuestas.map(({ tiene_respuestas, ...rest }) => rest);

        localStorage.setItem("encuestas", JSON.stringify(encuestasSinRespuestas));
        
        Swal.fire(
            '¡Eliminada!',
            'La encuesta ha sido eliminada correctamente.',
            'success'
        );
        

        renderEncuestas(getEncuestas());
    }

    renderEncuestas(getEncuestas());
});
