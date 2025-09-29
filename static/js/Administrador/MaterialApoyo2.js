document.addEventListener("DOMContentLoaded", function() {
  const selectMaterias = document.querySelector(".form-select");
  const inputMateria = document.getElementById("nombre");

  selectMaterias.addEventListener("change", function() {
    const materiaSeleccionada = selectMaterias.options[selectMaterias.selectedIndex].text;

    if (materiaSeleccionada !== "MATERIAS") {
      inputMateria.value = materiaSeleccionada;
    } else {
      inputMateria.value = "";
    }
  });
});
