function buscarDocente() {
  // Obtener el valor del input
  let input = document.getElementById("search");
  let filtro = input.value.toLowerCase();

  // Seleccionar la tabla y las filas
  let tabla = document.getElementById("tabla-docentes");
  let filas = tabla.getElementsByTagName("tr");

  // Recorrer todas las filas excepto el encabezado
  for (let i = 1; i < filas.length; i++) {
    let celdas = filas[i].getElementsByTagName("td");
    let encontrado = false;

    // Revisar cada celda de la fila
    for (let j = 0; j < celdas.length; j++) {
      let texto = celdas[j].textContent || celdas[j].innerText;
      if (texto.toLowerCase().indexOf(filtro) > -1) {
        encontrado = true;
        break;
      }
    }

    // Mostrar u ocultar fila
    filas[i].style.display = encontrado ? "" : "none";
  }
}