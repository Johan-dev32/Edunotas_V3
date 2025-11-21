const datosInasistencias = [
  {
    estudiante: "Juan Pérez",
    curso: "1002",
    fecha: "2025-09-28",
    razon: "Cita médica",
    archivo: "https://upload.wikimedia.org/wikipedia/en/0/05/Hello_kitty_character_portrait.png",
    estado: "Pendiente"
  },
  {
    estudiante: "María López",
    curso: "901",
    fecha: "2025-09-29",
    razon: "Calamidad familiar",
    archivo: "https://www.inspireuplift.com/resizer/?image=https://cdn.inspireuplift.com/uploads/images/seller_products/59330/1709049161_KITTY.png&width=800&height=800&quality=90&format=auto&fit=pad",
    estado: "Pendiente"
  },
  {
    estudiante: "Carlos Gómez",
    curso: "1102",
    fecha: "2025-09-30",
    razon: "Gripa fuerte",
    archivo: "https://i.pinimg.com/originals/4c/9c/51/4c9c518f8a52bfcbb5e3eac2de8f26dd.png",
    estado: "Pendiente"
  },
  {
    estudiante: "Ana Torres",
    curso: "803",
    fecha: "2025-10-01",
    razon: "Viaje familiar",
    archivo: "https://upload.wikimedia.org/wikipedia/en/0/0c/Hello_Kitty_1974.png",
    estado: "Pendiente"
  },
  {
    estudiante: "David Rodríguez",
    curso: "701",
    fecha: "2025-10-02",
    razon: "Consulta odontológica",
    archivo: "https://i.etsystatic.com/18930834/r/il/77e8d3/2456442681/il_794xN.2456442681_3w2v.jpg",
    estado: "Pendiente"
  },
  {
    estudiante: "Laura Sánchez",
    curso: "603",
    fecha: "2025-10-03",
    razon: "Accidente leve",
    archivo: "https://m.media-amazon.com/images/I/51syjM4S9DL._AC_UF894,1000_QL80_.jpg",
    estado: "Pendiente"
  },
  {
    estudiante: "Pedro Martínez",
    curso: "902",
    fecha: "2025-10-04",
    razon: "Problemas personales",
    archivo: "https://ih1.redbubble.net/image.2546065091.6234/flat,750x,075,f-pad,750x1000,f8f8f8.jpg",
    estado: "Pendiente"
  },
  {
    estudiante: "Sofía Ramírez",
    curso: "1001",
    fecha: "2025-10-05",
    razon: "Cita psicológica",
    archivo: "https://cdn.shopify.com/s/files/1/0553/2495/5721/files/hello-kitty-face_480x480.png?v=1631712435",
    estado: "Pendiente"
  },
  {
    estudiante: "Andrés Castillo",
    curso: "1102",
    fecha: "2025-10-06",
    razon: "Problemas de transporte",
    archivo: "https://www.pngmart.com/files/22/Hello-Kitty-PNG-Pic.png",
    estado: "Pendiente"
  },
  {
    estudiante: "Valentina Hernández",
    curso: "801",
    fecha: "2025-10-07",
    razon: "Dolor de cabeza",
    archivo: "https://png.pngtree.com/png-clipart/20230916/original/pngtree-hello-kitty-png-image_12228227.png",
    estado: "Pendiente"
  }
];

function renderTabla(data) {
  const tabla = document.getElementById("tablaInasistencias");
  tabla.innerHTML = "";
  data.forEach((item, index) => {
    tabla.innerHTML += `
      <tr>
        <td>${item.estudiante}</td>
        <td>${item.curso}</td>
        <td>${item.fecha}</td>
        <td>${item.razon}</td>
        <td>
          <a href="archivos/${item.archivo}" target="_blank">
            <i class="bi bi-file-earmark-pdf-fill" style="font-size: 24px; color: red;"></i>
          </a>
        </td>
        <td>${item.estado}</td>
        <td>
          <button class="aprobar" onclick="cambiarEstado(${index}, 'Aprobada')">Aprobar</button>
          <button class="rechazar" onclick="cambiarEstado(${index}, 'No aprobada')">No aprobar</button>
        </td>
      </tr>
    `;
  });
}

function cambiarEstado(index, nuevoEstado) {
  datosInasistencias[index].estado = nuevoEstado;
  renderTabla(datosInasistencias);
}

function aplicarFiltros() {
  const curso = document.getElementById("filterCurso").value.toLowerCase();
  const estudiante = document.getElementById("filterEstudiante").value.toLowerCase();
  const estado = document.getElementById("filterEstado").value;

  const filtrados = datosInasistencias.filter(item => {
    return (
      (curso === "" || item.curso.toLowerCase().includes(curso)) &&
      (estudiante === "" || item.estudiante.toLowerCase().includes(estudiante)) &&
      (estado === "" || item.estado === estado)
    );
  });

  renderTabla(filtrados);
}


renderTabla(datosInasistencias);
