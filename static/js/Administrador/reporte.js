document.getElementById("btnGenerar").addEventListener("click", () => {
  const materias = [
    { nombre: "Matemáticas", notas: [2.8, 3.0, 2.5, 3.2, 3.0] },
    { nombre: "Ciencias", notas: [4.2, 4.0, 4.5, 3.9, 4.3] },
    { nombre: "Inglés", notas: [3.5, 3.2, 3.8, 3.9, 3.7] }
  ];

  const cuerpo = document.getElementById("tablaNotas");
  cuerpo.innerHTML = "";

  materias.forEach(m => {
    const promedio = (m.notas.reduce((a,b)=>a+b,0)/m.notas.length).toFixed(2);
    const riesgo = promedio < 3.0;
    const fila = `
      <tr>
        <td>${m.nombre}</td>
        ${m.notas.map(n => `<td>${n}</td>`).join('')}
        <td class="${riesgo ? 'riesgo' : 'rendimiento'}">${promedio}</td>
        <td>${riesgo ? 'Materia en riesgo de pérdida' : 'Buen rendimiento académico'}</td>
      </tr>`;
    cuerpo.innerHTML += fila;
  });

  alert("✅ Reporte generado. Ahora puedes descargar el PDF.");
});


document.getElementById("btnPDF").addEventListener("click", async () => {
  const { jsPDF } = window.jspdf;
  const reporte = document.getElementById("reporte");


  const canvas = await html2canvas(reporte, { scale: 2 });
  const imgData = canvas.toDataURL("image/png");


  const pdf = new jsPDF("p", "mm", "a4");
  const pageWidth = pdf.internal.pageSize.getWidth();
  const imgWidth = pageWidth - 20; // márgenes
  const imgHeight = canvas.height * imgWidth / canvas.width;

  pdf.addImage(imgData, "PNG", 10, 10, imgWidth, imgHeight);

  const estudiante = document.getElementById("selectEstudiante").value.split(" - ")[0];
  pdf.save(`Reporte_${estudiante}.pdf`);
});
