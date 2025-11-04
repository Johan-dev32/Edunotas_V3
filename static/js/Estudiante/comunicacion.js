// Datos simulados (estos vendrían del servidor)
const envios = [
  {
    archivo: "Circular de Evaluaciones.pdf",
    profesor: "Profe Sandra Gómez",
    fecha: "02/11/2025",
    linkArchivo: "#",
    linkWhatsApp: "https://wa.me/573001112233?text=Hola%20profe!"
  },
  {
    archivo: "Recordatorio tareas semana 10.pdf",
    profesor: "Profe Carlos López",
    fecha: "30/10/2025",
    linkArchivo: "#",
    linkWhatsApp: "https://wa.me/573005556677?text=Consulta%20sobre%20tareas"
  },
  {
    archivo: "Citación Padres Noviembre.pdf",
    profesor: "Coordinación Académica",
    fecha: "28/10/2025",
    linkArchivo: "#",
    linkWhatsApp: "https://wa.me/573008887799?text=Citación"
  }
];

const tbody = document.querySelector("#tablaEnvios tbody");

envios.forEach(envio => {
  const tr = document.createElement("tr");

  tr.innerHTML = `
    <td>${envio.archivo}</td>
    <td>${envio.profesor}</td>
    <td>${envio.fecha}</td>
    <td>
      <button class="btn" onclick="abrirArchivo('${envio.linkArchivo}')">Ver documento</button>
      <button class="btn btn-whatsapp" onclick="abrirWhatsApp('${envio.linkWhatsApp}')">Ver en WhatsApp</button>
    </td>
  `;

  tbody.appendChild(tr);
});

function abrirArchivo(url) {
  window.open(url, "_blank");
}

function abrirWhatsApp(url) {
  window.open(url, "_blank");
}
