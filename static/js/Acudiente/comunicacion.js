// Datos simulados para el acudiente
const envios = [
  {
    archivo: "Circular sobre uniformes.pdf",
    profesor: "Coordinación de Convivencia",
    fecha: "01/11/2025",
    linkArchivo: "#",
    linkWhatsApp: "https://wa.me/573001112233?text=Consulta%20sobre%20uniformes"
  },
  {
    archivo: "Citación padres de familia.pdf",
    profesor: "Rectoría",
    fecha: "30/10/2025",
    linkArchivo: "#",
    linkWhatsApp: "https://wa.me/573002223344?text=Confirmo%20asistencia"
  },
  {
    archivo: "Boletín académico tercer periodo.pdf",
    profesor: "Coordinación Académica",
    fecha: "27/10/2025",
    linkArchivo: "#",
    linkWhatsApp: "https://wa.me/573003335566?text=Consulta%20boletín"
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
