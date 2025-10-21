const btnEscuchar = document.getElementById("btnEscuchar");
    const descripcion = `{{ descripcion_actividad or 'Aquí el docente deja las instrucciones de la tarea.' }}`;
    const pdfInput = document.getElementById("pdfUpload");
    const archivoSubido = document.getElementById("archivoSubido");
    const btnEntregar = document.getElementById("btnEntregar");
    const btnCancelar = document.getElementById("btnCancelar");
    const estadoEntrega = document.getElementById("estadoEntrega");

    // 🔊 Leer tarea en voz alta
    btnEscuchar.addEventListener("click", () => {
      const speech = new SpeechSynthesisUtterance(descripcion);
      speech.lang = "es-ES";
      speech.rate = 1;
      window.speechSynthesis.speak(speech);
    });

    // 📂 Mostrar nombre del PDF
    pdfInput.addEventListener("change", () => {
      const archivo = pdfInput.files[0];
      if (archivo) {
        archivoSubido.textContent = `Archivo seleccionado: ${archivo.name}`;
      }
    });

    // ✅ Entregar tarea con confirmación
    btnEntregar.addEventListener("click", () => {
      if (!pdfInput.files.length) {
        alert("Por favor, selecciona un archivo PDF antes de entregar.");
        return;
      }

      if (confirm("¿Estás seguro de que deseas entregar esta tarea?")) {
        estadoEntrega.textContent = "✅ Has entregado la tarea con éxito.";
        estadoEntrega.classList.add("text-success");
        btnCancelar.classList.remove("d-none");
        btnEntregar.disabled = true;
      }
    });

    // ❌ Cancelar entrega
    btnCancelar.addEventListener("click", () => {
      if (confirm("¿Deseas cancelar la entrega?")) {
        estadoEntrega.textContent = "⚠️ Has anulado tu entrega.";
        estadoEntrega.classList.remove("text-success");
        estadoEntrega.classList.add("text-danger");
        btnEntregar.disabled = false;
        btnCancelar.classList.add("d-none");
      }
    });