// NoticiasVistas.js

document.addEventListener("DOMContentLoaded", function() {
    // Si Bootstrap no se ha cargado, intentamos forzar la carga de noticias de todos modos.
    cargarNoticias();
});

// Referencias a los elementos del modal (deben ser globales para usarse en la función de llenado)
const modalTitle = document.getElementById('noticiaModalLabel');
const modalImagen = document.getElementById('modalImagen');
const modalCreadoPor = document.getElementById('modalCreadoPor');
const modalFecha = document.getElementById('modalFecha');
const modalRedaccion = document.getElementById('modalRedaccion');


async function cargarNoticias() {
    const contenedor = document.getElementById("noticiasContainer");
    if (!contenedor) return;
    contenedor.innerHTML = `<p class="text-center text-muted">Cargando noticias...</p>`;

    try {
        const res = await fetch("/administrador/noticias/historial");
        const data = await res.json();

        if (data.success) {
            let noticias = data.noticias;
            const noticiasRecientes = noticias.slice(0, 4); // Límite de 4 noticias

            contenedor.innerHTML = ''; // Limpiar después de cargar
            
            noticiasRecientes.forEach(noticia => {
                const col = document.createElement('div');
                col.className = 'col-md-6 col-lg-3 d-flex align-items-stretch';
                
                // 📌 Guardamos TODOS los datos en el elemento del DOM (data-atributos)
                col.setAttribute('data-id', noticia.id);
                col.setAttribute('data-titulo', noticia.titulo);
                col.setAttribute('data-redaccion', noticia.redaccion); // <-- Texto completo
                col.setAttribute('data-creado_por', noticia.creado_por);
                col.setAttribute('data-fecha', noticia.fecha);
                col.setAttribute('data-archivo_url', noticia.archivo_url || '');

                const imagenURL = noticia.archivo_url || '';
                const imagenHTML = imagenURL
                    ? `<img src="${imagenURL}" class="card-img-top" alt="Imagen de la noticia" style="height: 200px; object-fit: cover;">`
                    : `<div class="placeholder-img d-flex align-items-center justify-content-center bg-light text-muted" style="height: 200px; border-bottom: 1px solid #ddd;">Sin Imagen</div>`;

                col.innerHTML = `
                    <div class="card shadow-sm w-100 noticia-card" style="cursor: pointer;" 
                         data-bs-toggle="modal" data-bs-target="#noticiaModal">
                        ${imagenHTML}
                        <div class="card-body d-flex flex-column">
                            <h5 class="card-title fw-bold">${noticia.titulo}</h5>
                            <p class="card-text">${noticia.redaccion.substring(0, 80)}...</p> 
                            
                            <div class="mt-auto pt-2 border-top">
                                <small class="text-muted d-block">Publicado por: ${noticia.creado_por}</small>
                                <small class="text-muted d-block">Fecha: ${noticia.fecha}</small>
                            </div>
                        </div>
                    </div>
                `;
                contenedor.appendChild(col);
            });
            
            // 📌 Agregar el evento de clic a TODAS las tarjetas
            // El clic ahora solo llama a la función de llenado. El modal se abre con los data-atributos.
            document.querySelectorAll('.noticia-card').forEach(card => {
                // Buscamos el elemento padre con los data-atributos
                const parentCol = card.closest('.col-md-6'); 
                
                card.addEventListener('click', function() {
                    mostrarNoticiaCompleta(parentCol);
                });
            });


        } else {
            contenedor.innerHTML = `<p class="alert alert-warning">${data.error || "Error al cargar las noticias."}</p>`;
        }

    } catch (error) {
        console.error("Error al conectar con el historial:", error);
        contenedor.innerHTML = `<p class="alert alert-danger">🛑 Error crítico al cargar datos del servidor.</p>`;
    }
}

// 📌 Función para mostrar la información completa en el modal
// Recibe el elemento que contiene los data-atributos
function mostrarNoticiaCompleta(cardElement) {
    
    // Obtener datos del data-attribute
    const titulo = cardElement.getAttribute('data-titulo');
    const redaccion = cardElement.getAttribute('data-redaccion');
    const creadoPor = cardElement.getAttribute('data-creado_por');
    const fecha = cardElement.getAttribute('data-fecha');
    const imagenURL = cardElement.getAttribute('data-archivo_url');
    
    // Llenar el modal
    modalTitle.textContent = titulo;
    modalCreadoPor.textContent = creadoPor;
    modalFecha.textContent = fecha;
    modalRedaccion.textContent = redaccion;
    
    // Configurar la imagen
    if (imagenURL) {
        modalImagen.src = imagenURL;
        modalImagen.style.display = 'block';
    } else {
        // Usar una imagen de placeholder si no hay URL (opcional)
        // Ocultar la imagen si no existe
        modalImagen.style.display = 'none'; 
    }
    
    // **NOTA:** El modal se abre automáticamente gracias a data-bs-toggle y data-bs-target
    // en la estructura HTML de la tarjeta, ¡no necesitamos llamarlo aquí!
}