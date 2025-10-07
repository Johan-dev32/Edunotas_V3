document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector("form");
  const historyBody = document.getElementById("historyBody");

  let historial = JSON.parse(localStorage.getItem("historialEnvios")) || [];
  renderHistorial();

  form.addEventListener("submit", (e) => {
    e.preventDefault(); // evita que recargue

    const formData = new FormData(form);

    fetch("{{ url_for('Administrador.enviar_correo') }}", {
      method: "POST",
      body: formData
    })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        const registro = {
          destinatario: formData.get("destinatario"),
          curso: formData.get("curso"),
          tipo: formData.get("tipo"),
          archivo: formData.get("archivo") ? formData.get("archivo").name : "Sin archivo",
          fecha: new Date().toLocaleString(),
          estado: "Enviado"
        };
        historial.push(registro);
        localStorage.setItem("historialEnvios", JSON.stringify(historial));
        renderHistorial();
        form.reset();
      } else {
        alert("Error: " + data.message);
      }
    })
    .catch(err => console.error("Error:", err));
  });

  function renderHistorial() {
    historyBody.innerHTML = "";
    historial.forEach((reg) => {
      const fila = `
        <tr>
          <td>📎 ${reg.archivo}</td>
          <td>${reg.curso}</td>
          <td>${reg.tipo}</td>
          <td>${reg.destinatario}</td>
          <td>${reg.fecha}</td>
          <td>${reg.estado}</td>
        </tr>`;
      historyBody.insertAdjacentHTML("beforeend", fila);
    });
  }
});

