document.getElementById("btnPDF").addEventListener("click", () => {
  const fecha = document.getElementById("fecha").value;
  const autor = document.getElementById("autor").value;
  const titulo = document.getElementById("titulo").value;
  const redaccion = document.getElementById("redaccion").value;

  const { jsPDF } = window.jspdf;
  const doc = new jsPDF();

  // Encabezado
  doc.setFontSize(18);
  doc.setFont("helvetica", "bold");
  doc.text("Resumen Semanal", 105, 20, { align: "center" });

  doc.setFontSize(12);
  doc.setFont("helvetica", "normal");

  // Datos generales
  doc.text(` Fecha: ${fecha}`, 20, 40);
  doc.text(` Autor: ${autor}`, 20, 50);
  doc.text(` Título: ${titulo}`, 20, 60);

  // Separador
  doc.line(20, 70, 190, 70);

  // Actividades
  doc.setFont("helvetica", "bold");
  doc.text("Actividades realizadas:", 20, 85);

  doc.setFont("helvetica", "normal");

  // Texto multilínea (ajusta al ancho de la página)
  const textoActividades = doc.splitTextToSize(redaccion, 170);
  doc.text(textoActividades, 20, 95);

  // Descargar PDF
  doc.save("resumen_semanal.pdf");
});
