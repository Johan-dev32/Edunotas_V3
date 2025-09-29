
document.addEventListener("DOMContentLoaded", () => {
  const addBtn = document.querySelector(".add");
  if (addBtn) {
    addBtn.addEventListener("click", () => {
      const modal = new bootstrap.Modal(document.getElementById("agregarModal"));
      modal.show();
    });
  }
});

// Buscar acudiente en la tabla
function buscarAcudiente() {
  let input = document.getElementById("search").value.toLowerCase();
  let rows = document.querySelectorAll("table tbody tr");

  rows.forEach(row => {
    let texto = row.innerText.toLowerCase();
    row.style.display = texto.includes(input) ? "" : "none";
  });

}