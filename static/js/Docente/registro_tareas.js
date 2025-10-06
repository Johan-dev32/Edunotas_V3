const tareas = {
  espanol: [
    "Leer capítulo 1 de la novela",
    "Escribir resumen de la lectura",
    "Ejercicios de ortografía",
    "Redacción de párrafo descriptivo",
    "Presentación oral"
  ],
  matematicas: [
    "Resolver problemas de álgebra",
    "Practicar tablas de multiplicar",
    "Preparar presentación sobre geometría",
    "Ejercicios de fracciones",
    "Problemas de porcentajes"
  ],
  ciencias: [
    "Experimento de plantas",
    "Investigar sobre el sistema solar",
    "Responder cuestionario de química",
    "Crear maqueta del sistema digestivo",
    "Informe sobre energías renovables"
  ],
  historia: [
    "Investigar sobre la independencia",
    "Hacer línea de tiempo de eventos",
    "Resumen de la Revolución Industrial",
    "Mapa histórico de América Latina",
    "Ensayo sobre historia contemporánea"
  ]
};

const selectBar = document.getElementById('asignaturaSelectBar');
const tareasContainer = document.getElementById('tareasContainer');
const tituloSub = document.getElementById('titulo-sub');

function mostrarTareas(asignatura) {
  tareasContainer.innerHTML = '';

  // Actualizar subtitulo
  tituloSub.textContent = `TAREAS DE ${asignatura.toUpperCase()} 1P`;

  if (tareas[asignatura]) {
    tareas[asignatura].forEach((tarea, index) => {
      const div = document.createElement('div');
      div.className = 'actividad';
      div.innerHTML = `
        <span>ACT ${index + 1}</span>
        <button>Ver Detalles</button>
        <p style="margin-top:10px;">${tarea}</p>
      `;
      tareasContainer.appendChild(div);
    });
  }
}

// Mostrar inicialmente Español
mostrarTareas('espanol');

// Cambiar tareas al seleccionar otra asignatura
selectBar.addEventListener('change', (e) => {
  mostrarTareas(e.target.value);
});