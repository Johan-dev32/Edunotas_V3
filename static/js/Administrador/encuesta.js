const preguntasContainer = document.getElementById("preguntasContainer");
const btnAgregar = document.getElementById("agregarPregunta");
const form = document.getElementById("encuestaForm");
const imgInput = document.getElementById("imgInput");
const imgPreview = document.getElementById("imgPreview");


let contadorPreguntas = 0;
const materias = [
    "ESPAÑOL", "MATEMÁTICAS", "INGLÉS", "SOCIALES", "ÉTICA", "FILOSOFÍA", 
    "EDUCACIÓN FÍSICA", "ARTÍSTICA", "BIOLÓGICA - FÍSICA - QUÍMICA", 
    "RELIGIÓN", "TECNOLOGÍA - INFORMÁTICA", "P.T.I"
];


function getUrlParameter(name) {
    name = name.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]');
    var regex = new RegExp('[\\?&]' + name + '=([^&#]*)');
    var results = regex.exec(location.search);
    return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '));
}

const encuestaIdToEdit = getUrlParameter('id'); 
let isEditing = !!encuestaIdToEdit;
let encuestaOriginal = null;


const materiaSelect = document.getElementById("materiaSelect");
materias.forEach(m => {
    let opt = document.createElement("option");
    opt.value = m;
    opt.textContent = m;
    materiaSelect.appendChild(opt);
});

document.getElementById("chkDoc").addEventListener("change", e => {
    materiaSelect.classList.toggle("d-none", !e.target.checked);
});

function configurarGradoCurso(chkId, gradoSelectId, cursoSelectId) {
    const chk = document.getElementById(chkId);
    const gradoSelect = document.getElementById(gradoSelectId);
    const cursoSelect = document.getElementById(cursoSelectId);

    gradoSelect.innerHTML = `<option value="">Seleccione grado</option>`;
    for (let g = 6; g <= 11; g++) {
        let opt = document.createElement("option");
        opt.value = g;
        opt.textContent = g;
        gradoSelect.appendChild(opt);
    }

    chk.addEventListener("change", e => {
        const activo = e.target.checked;
        gradoSelect.classList.toggle("d-none", !activo);
        cursoSelect.classList.toggle("d-none", !activo);
        if (!activo) {
            gradoSelect.value = "";
            cursoSelect.innerHTML = `<option value="">Seleccione curso</option>`;
        }
    });

    gradoSelect.addEventListener("change", () => {
        cursoSelect.innerHTML = `<option value="">Seleccione curso</option>`;
        if (gradoSelect.value) {
            const gradoNum = parseInt(gradoSelect.value);
            [1, 2, 3].forEach(c => {
                let cursoCode = `${gradoNum}0${c}`;
                let opt = document.createElement("option");
                opt.value = cursoCode;
                opt.textContent = cursoCode;
                cursoSelect.appendChild(opt);
            });
        }
    });
}

configurarGradoCurso("chkEst", "gradoSelectEst", "cursoSelectEst");
configurarGradoCurso("chkAcu", "gradoSelectAcu", "cursoSelectAcu");


function agregarOpcion(tipo, contenedor, valorInicial = "") {
    const wrapper = document.createElement("div");
    wrapper.classList.add("input-group", "mb-2");
    wrapper.innerHTML = `
      <div class="input-group-text">
        <input type="${tipo}" disabled>
      </div>
      <input type="text" class="form-control opcionInput" placeholder="Ingrese respuesta" value="${valorInicial}">
      <button type="button" class="btn btn-outline-danger btn-sm btnEliminarOpcion" title="Eliminar opción">
        <i class="bi bi-trash-fill"></i>
      </button>
    `;

    wrapper.querySelector(".btnEliminarOpcion").addEventListener("click", () => {
        wrapper.remove();
    });

    contenedor.appendChild(wrapper);
}

function renderOpciones(tipo, contenedor) {
    contenedor.innerHTML = "";
    if (tipo === "radio" || tipo === "checkbox") {
        if (!isEditing) {
            agregarOpcion(tipo, contenedor);
            agregarOpcion(tipo, contenedor);
        }
    } else if (tipo === "text") {
        contenedor.innerHTML = `<input type="text" class="form-control" placeholder="Espacio de Respuesta" disabled>`;
    }
}


function crearCajaPregunta(preguntaData = null) {
    contadorPreguntas++;
    const div = document.createElement("div");
    div.classList.add("pregunta-box", "mb-3"); 
    div.dataset.preguntaId = contadorPreguntas; 

    const textoPregunta = preguntaData ? preguntaData.texto : "";
    const tipoRespuesta = preguntaData ? preguntaData.tipo : "radio";
    
    div.innerHTML = `
        <div class="d-flex justify-content-between align-items-center mb-2">
            <label class="fw-bold">Pregunta ${contadorPreguntas}:</label>
            <button type="button" class="btn btn-sm btn-danger btnEliminarPregunta"><i class="bi bi-x-lg"></i></button>
        </div>
        
        <input type="text" class="form-control mb-2 preguntaInput" placeholder="Ingrese la pregunta" value="${textoPregunta}">
        
        <select class="form-select tipoRespuesta mb-2">
            <option value="radio" ${tipoRespuesta === 'radio' ? 'selected' : ''}>Selección Única</option>
            <option value="checkbox" ${tipoRespuesta === 'checkbox' ? 'selected' : ''}>Selección Múltiple</option>
            <option value="text" ${tipoRespuesta === 'text' ? 'selected' : ''}>Texto Libre</option>
        </select>

        <div class="respuestas-container"></div>
        <button type="button" class="btn btn-sm btn-secondary mt-2 btnAgregarOpcion">+ Agregar Opción</button>
    `;

    preguntasContainer.appendChild(div);

    const tipoSelect = div.querySelector(".tipoRespuesta");
    const respuestasContainer = div.querySelector(".respuestas-container");
    const btnAgregarOpcion = div.querySelector(".btnAgregarOpcion");
    const btnEliminarPregunta = div.querySelector(".btnEliminarPregunta");
    
    if (preguntaData && preguntaData.tipo !== 'text' && preguntaData.opciones.length > 0) {
        respuestasContainer.innerHTML = "";
        preguntaData.opciones.forEach(opcionTexto => {
            agregarOpcion(preguntaData.tipo, respuestasContainer, opcionTexto);
        });
    } else {
        renderOpciones(tipoRespuesta, respuestasContainer);
    }

    tipoSelect.addEventListener("change", () => {
        renderOpciones(tipoSelect.value, respuestasContainer);
    });

    btnAgregarOpcion.addEventListener("click", () => {
        if (tipoSelect.value === "text") {
            alert("El tipo Texto Libre no necesita opciones.");
            return;
        }
        agregarOpcion(tipoSelect.value, respuestasContainer);
    });

    btnEliminarPregunta.addEventListener("click", () => {
        div.remove();
    });
}



function loadEncuestaForEditing(id) {
    const encuestas = JSON.parse(localStorage.getItem("encuestas")) || [];
    // Uso de parseInt para asegurar la comparación correcta
    const encuesta = encuestas.find(e => e.id === parseInt(id)); 

    if (!encuesta) {
        alert("Encuesta no encontrada.");
        isEditing = false;
        return;
    }

    encuestaOriginal = encuesta; 
    
    document.getElementById("formTitle").textContent = "Editar Encuesta";
    document.getElementById("formDescription").textContent = "Modifique la encuesta y guarde los cambios.";

    document.getElementById("fechaCierre").value = encuesta.fechaCierre;
    document.getElementById("tituloEncuesta").value = encuesta.titulo;
    
    document.querySelectorAll(".targetChk").forEach(chk => chk.checked = false);
    
    encuesta.usuarios.forEach(usuario => {
        const chk = document.querySelector(`.targetChk[value="${usuario}"]`);
        if (chk) {
            chk.checked = true;
            chk.dispatchEvent(new Event('change')); 
        }
    });

    preguntasContainer.innerHTML = "";
    contadorPreguntas = 0; 
    encuesta.preguntas.forEach(p => {
        crearCajaPregunta(p); 
    });

    // 5. Cambiar texto del botón de Enviar
    document.querySelector('button[type="submit"]').textContent = "Guardar Cambios";
}


if (isEditing) {
    loadEncuestaForEditing(encuestaIdToEdit);
}


btnAgregar.addEventListener("click", () => {
    crearCajaPregunta();
});

imgInput.addEventListener("change", e => {
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = () => {
            imgPreview.innerHTML = `<img src="${reader.result}" style="max-width:100%; max-height:100%">`;
        };
        reader.readAsDataURL(file);
    } else {
        imgPreview.textContent = "Sin imagen";
    }
});


form.addEventListener("submit", (e) => {
    e.preventDefault();

    const fecha = document.getElementById("fechaCierre").value;
    const titulo = document.getElementById("tituloEncuesta").value;
    const usuarios = [...document.querySelectorAll(".targetChk:checked")].map(el => el.value);

    if (!fecha) { alert("Debe seleccionar una fecha de cierre."); return; }
    if (!titulo.trim()) { alert("Debe ingresar un título."); return; }
    if (usuarios.length === 0) { alert("Debe seleccionar al menos un destinatario."); return; }
    if (document.querySelectorAll(".pregunta-box").length === 0) { alert("Debe agregar al menos una pregunta."); return; }

    const preguntas = [];
    let preguntasVacias = false;
    document.querySelectorAll(".pregunta-box").forEach(box => {
        const texto = box.querySelector(".preguntaInput").value;
        const tipo = box.querySelector(".tipoRespuesta").value;
        const opciones = [...box.querySelectorAll(".opcionInput")].map(i => i.value);
        if (!texto.trim()) preguntasVacias = true;
        preguntas.push({ texto, tipo, opciones: tipo === "text" ? [] : opciones });
    });

    if (preguntasVacias) { alert("Hay preguntas sin texto."); return; }

    const nuevaEncuesta = {
        id: isEditing ? parseInt(encuestaIdToEdit) : Date.now(),
        fechaCierre: fecha,
        titulo: titulo,
        usuarios,
        preguntas,
    };

    let encuestas = JSON.parse(localStorage.getItem("encuestas")) || [];
    if (isEditing) {
        const index = encuestas.findIndex(e => e.id === nuevaEncuesta.id);
        if (index !== -1) {
            encuestas[index] = nuevaEncuesta;
            localStorage.setItem("encuestas", JSON.stringify(encuestas));
            alert("¡Cambios guardados correctamente!"); // <-- mensaje en lugar de redirección
        } else {
            alert("No se encontró la encuesta original.");
            return;
        }
    } else {
        encuestas.push(nuevaEncuesta);
        localStorage.setItem("encuestas", JSON.stringify(encuestas));
        alert("Encuesta creada correctamente.");
        form.reset();
        preguntasContainer.innerHTML = "";
        imgPreview.textContent = "Sin imagen";
        contadorPreguntas = 0;
    }
});
