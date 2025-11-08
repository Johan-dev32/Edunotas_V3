document.addEventListener("DOMContentLoaded", function() {
    const resumenForm = document.getElementById("resumenForm");
    const btnPDF = document.getElementById("btnPDF");

    // --- Función de ayuda para Generar el PDF ---
    function generarPDF(fecha, autor, titulo, redaccion) {
        const { jsPDF } = window.jspdf;
        const doc = new jsPDF();

        doc.setFontSize(18);
        doc.setFont("helvetica", "bold");
        doc.text("Resumen Semanal", 105, 20, { align: "center" });

        doc.setFontSize(12);
        doc.setFont("helvetica", "normal");

        doc.text(`Fecha: ${fecha}`, 20, 40);
        doc.text(`Autor: ${autor}`, 20, 50);
        doc.text(`Título: ${titulo}`, 20, 60);

        doc.line(20, 70, 190, 70);

        doc.setFont("helvetica", "bold");
        doc.text("Actividades realizadas:", 20, 85);

        doc.setFont("helvetica", "normal");
        const textoActividades = doc.splitTextToSize(redaccion, 170);
        doc.text(textoActividades, 20, 95);

        doc.save(`resumen_semanal_${fecha}.pdf`);
    }

    // --- Listener para el botón Generar PDF (Envío a DB + PDF) ---
    btnPDF.addEventListener("click", async (e) => {
        
        // Obtenemos los valores del formulario
        const fecha = document.getElementById("fecha").value;
        const autor = document.getElementById("autor").value; // Nombre del autor
        const titulo = document.getElementById("titulo").value;
        const redaccion = document.getElementById("redaccion").value;

        // Validación
        if (!fecha || !autor || !titulo || !redaccion) {
            alert("⚠️ Por favor, complete todos los campos requeridos.");
            return;
        }

        // Crear FormData para enviar los datos a Flask
        const formData = new FormData(resumenForm);
        
        try {
            // 1. Enviar datos a la base de datos
            const res = await fetch("/administrador/resumensemanal/registro", {
                method: "POST",
                body: formData,
            });

            const data = await res.json();

            if (res.ok && data.success) {
                
                // 2. Si es exitoso, generar el PDF
                generarPDF(fecha, autor, titulo, redaccion);

                alert("✅ Resumen semanal guardado en la Base de Datos y PDF generado.");
                
                // Limpiar formulario
                resumenForm.reset(); 
                
            } else {
                // Manejar errores de validación o del servidor
                alert("❌ Error al guardar el resumen: " + (data.error || "Fallo desconocido."));
            }

        } catch (error) {
            console.error("Error de conexión:", error);
            alert("🛑 Error de conexión. No se pudo guardar el resumen en el servidor.");
        }
    });

});