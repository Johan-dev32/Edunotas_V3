document.addEventListener("DOMContentLoaded", () => {
  const selectPeriodo = document.getElementById("selectPeriodo");

  selectPeriodo.addEventListener("change", () => {
    const periodo = selectPeriodo.value;
    const url = selectPeriodo.dataset.url;

    if (["1", "2", "3", "4"].includes(periodo)) {
      // Redirige a la vista con el período como parámetro
      window.location.href = `${url}?periodo=${periodo}`;
    } else {
      alert("Seleccione un período válido.");
    }
  });
});
