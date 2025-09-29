document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("registroForm");
  const mensajeExito = document.getElementById("mensajeExito");

  const nombres = document.getElementById("nombres");
  const apellidos = document.getElementById("apellidos");
  const correoPersonal = document.getElementById("correoPersonal");
  const correoInstitucional = document.getElementById("correoInstitucional");
  const contrasena = document.getElementById("contrasena");
  const confirmarContrasena = document.getElementById("confirmarContrasena"); // NUEVO
  const numDoc = document.getElementById("numDoc");
  const telefono = document.getElementById("telefono");


  const departamento = document.getElementById("departamento");
  const ciudad = document.getElementById("ciudad");

  function mostrarError(id, mensaje) {
    const errorSpan = document.getElementById(id);
    if (errorSpan) errorSpan.textContent = mensaje;
  }

  function limpiarErrores() {
    document.querySelectorAll(".error").forEach(el => (el.textContent = ""));
  }

  const soloLetras = /^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/;
  const soloNumeros = /^[0-9]+$/;

  nombres.addEventListener("input", function () {
    if (!soloLetras.test(this.value) && this.value !== "") {
      mostrarError("errorNombres", "Solo se permiten letras");
    } else {
      mostrarError("errorNombres", "");
    }
    this.value = this.value.replace(/[^a-zA-ZáéíóúÁÉÍÓÚñÑ\s]/g, "");
  });

  apellidos.addEventListener("input", function () {
    if (!soloLetras.test(this.value) && this.value !== "") {
      mostrarError("errorApellidos", "Solo se permiten letras");
    } else {
      mostrarError("errorApellidos", "");
    }
    this.value = this.value.replace(/[^a-zA-ZáéíóúÁÉÍÓÚñÑ\s]/g, "");
  });

  numDoc.addEventListener("input", function () {
    if (!soloNumeros.test(this.value) && this.value !== "") {
      mostrarError("errorNumDoc", "Solo se permiten números");
    } else {
      mostrarError("errorNumDoc", "");
    }
    this.value = this.value.replace(/\D/g, "");
  });

  telefono.addEventListener("input", function () {
    if (!soloNumeros.test(this.value) && this.value !== "") {
      mostrarError("errorTelefono", "Solo se permiten números");
    } else {
      mostrarError("errorTelefono", "");
    }
    this.value = this.value.replace(/\D/g, "");
  });


  if (confirmarContrasena) {
    const checkPasswords = () => {
      if (contrasena.value && confirmarContrasena.value && contrasena.value !== confirmarContrasena.value) {
        mostrarError("errorConfirmarContrasena", "Las contraseñas no coinciden");
      } else {
        mostrarError("errorConfirmarContrasena", "");
      }
    };
    contrasena.addEventListener("input", checkPasswords);
    confirmarContrasena.addEventListener("input", checkPasswords);
  }

  const ciudadesPorDepto = {
    "Amazonas": ["Leticia", "Puerto Nariño", "Tarapacá"],
    "Antioquia": ["Medellín", "Bello", "Itagüí", "Envigado", "Rionegro", "Apartadó"],
    "Arauca": ["Arauca", "Tame", "Saravena", "Arauquita"],
    "Atlántico": ["Barranquilla", "Soledad", "Malambo", "Puerto Colombia", "Galapa"],
    "Bolívar": ["Cartagena", "Magangué", "Turbaco", "Arjona"],
    "Boyacá": ["Tunja", "Sogamoso", "Duitama", "Chiquinquirá"],
    "Caldas": ["Manizales", "La Dorada", "Chinchiná", "Villamaría"],
    "Caquetá": ["Florencia", "San Vicente del Caguán", "Puerto Rico"],
    "Casanare": ["Yopal", "Aguazul", "Paz de Ariporo", "Villanueva"],
    "Cauca": ["Popayán", "Santander de Quilichao", "Puerto Tejada", "Piendamó"],
    "Cesar": ["Valledupar", "Aguachica", "Bosconia", "La Jagua de Ibirico"],
    "Chocó": ["Quibdó", "Istmina", "Tadó", "Condoto"],
    "Córdoba": ["Montería", "Cereté", "Sahagún", "Lorica"],
    "Cundinamarca": ["Soacha", "Zipaquirá", "Fusagasugá", "Girardot", "Chía", "Facatativá"],
    "Guainía": ["Inírida", "Barranco Minas", "Cacahual"],
    "Guaviare": ["San José del Guaviare", "El Retorno", "Calamar", "Miraflores"],
    "Huila": ["Neiva", "Pitalito", "Garzón", "La Plata"],
    "La Guajira": ["Riohacha", "Maicao", "Uribia", "Albania"],
    "Magdalena": ["Santa Marta", "Ciénaga", "Fundación", "El Banco"],
    "Meta": ["Villavicencio", "Acacías", "Granada", "Puerto López"],
    "Nariño": ["Pasto", "Tumaco", "Ipiales", "Túquerres"],
    "Norte de Santander": ["Cúcuta", "Ocaña", "Villa del Rosario", "Los Patios"],
    "Putumayo": ["Mocoa", "Puerto Asís", "Orito", "Villagarzón"],
    "Quindío": ["Armenia", "Calarcá", "La Tebaida", "Quimbaya"],
    "Risaralda": ["Pereira", "Dosquebradas", "Santa Rosa de Cabal", "La Virginia"],
    "San Andrés y Providencia": ["San Andrés", "Providencia", "Santa Catalina"],
    "Santander": ["Bucaramanga", "Floridablanca", "Girón", "Piedecuesta", "Barrancabermeja"],
    "Sucre": ["Sincelejo", "Corozal", "Tolú", "San Onofre"],
    "Tolima": ["Ibagué", "Espinal", "Melgar", "Honda"],
    "Valle del Cauca": ["Cali", "Palmira", "Buenaventura", "Tuluá", "Buga", "Yumbo", "Jamundí"],
    "Vaupés": ["Mitú", "Carurú", "Taraira"],
    "Vichada": ["Puerto Carreño", "La Primavera", "Santa Rosalía", "Cumaribo"],
    "Bogotá, D.C.": ["Bogotá"]
  };


  if (departamento) {

    const keys = Object.keys(ciudadesPorDepto).sort((a, b) => a.localeCompare(b, "es"));
    keys.forEach(dep => {
      const opt = document.createElement("option");
      opt.value = dep;
      opt.textContent = dep;
      departamento.appendChild(opt);
    });
  }


  if (departamento && ciudad) {
    departamento.addEventListener("change", function () {
      ciudad.innerHTML = '<option value="">Seleccione una ciudad</option>';
      const lista = ciudadesPorDepto[this.value] || [];
      lista.forEach(c => {
        const option = document.createElement("option");
        option.value = c;
        option.textContent = c;
        ciudad.appendChild(option);
      });
      ciudad.disabled = lista.length === 0;

      mostrarError("errorDepartamento", "");
      mostrarError("errorCiudad", "");
    });
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    let valido = true;
    limpiarErrores();

    const formatoCorreo = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (nombres.value.trim() === "") {
      mostrarError("errorNombres", "Este campo es obligatorio");
      valido = false;
    }

    if (apellidos.value.trim() === "") {
      mostrarError("errorApellidos", "Este campo es obligatorio");
      valido = false;
    }

    if (!formatoCorreo.test(correoPersonal.value.trim())) {
      mostrarError("errorCorreoPersonal", "Correo inválido");
      valido = false;
    }

    if (!formatoCorreo.test(correoInstitucional.value.trim())) {
      mostrarError("errorCorreoInstitucional", "Correo inválido");
      valido = false;
    }

    if (contrasena.value.trim().length < 8) {
      mostrarError("errorContrasena", "Mínimo 8 caracteres");
      valido = false;
    }


    if (!confirmarContrasena.value || contrasena.value !== confirmarContrasena.value) {
      mostrarError("errorConfirmarContrasena", "Las contraseñas no coinciden");
      valido = false;
    }

    const docSeleccionado = document.querySelector('input[name="doc"]:checked');
    if (!docSeleccionado) {
      mostrarError("errorDoc", "Seleccione un tipo de documento");
      valido = false;
    }

    if (numDoc.value.trim() === "") {
      mostrarError("errorNumDoc", "Este campo es obligatorio");
      valido = false;
    }

    if (telefono.value.trim() === "") {
      mostrarError("errorTelefono", "Este campo es obligatorio");
      valido = false;
    }

   
    if (!departamento.value) {
      mostrarError("errorDepartamento", "Seleccione un departamento");
      valido = false;
    }
    if (!ciudad.value) {
      mostrarError("errorCiudad", "Seleccione una ciudad");
      valido = false;
    }

    const sexoSeleccionado = document.querySelector('input[name="sexo"]:checked');
    if (!sexoSeleccionado) {
      mostrarError("errorSexo", "Seleccione un sexo");
      valido = false;
    }

    const rolSeleccionado = document.querySelector('input[name="rol"]:checked');
    if (!rolSeleccionado) {
      mostrarError("errorRol", "Seleccione un rol");
      valido = false;
    }

    if (valido) {
      mensajeExito.style.display = "block";
      setTimeout(() => (mensajeExito.style.display = "none"), 5000);
      form.reset();
    
      ciudad.innerHTML = '<option value="">Seleccione una ciudad</option>';
      ciudad.disabled = true;
    }
  });
});