document.addEventListener('DOMContentLoaded', () => {
  const cursoId = window.CURSO_ID || null;
  const selPeriodo = document.getElementById('selPeriodo');
  const selCurso = document.getElementById('selCurso');
  const btnRefrescar = document.getElementById('btnRefrescar');

  const tablaGrupoBody = document.querySelector('#tablaGrupo tbody');
  const tablaEstBody = document.querySelector('#tablaEstudiantes tbody');
  const btnPDF = document.getElementById('btnPDF');
  const btnExcel = document.getElementById('btnExcel');

  const ctxAcad = document.getElementById('graficaAcademica').getContext('2d');
  const ctxAsis = document.getElementById('graficaAsistencia').getContext('2d');
  const ctxDisc = document.getElementById('graficaConducta').getContext('2d');

  let chartAcad, chartAsis, chartDisc;

  const fetchJson = async (url) => {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  };

  const cargarDatos = async () => {
    const selectedCurso = selCurso && selCurso.value ? selCurso.value : (cursoId || '');
    if (!selectedCurso) return;
    const periodo = selPeriodo.value || '';
    const url = `/administrador/informe/datos?curso_id=${encodeURIComponent(selectedCurso)}${periodo ? `&periodo=${periodo}` : ''}`;
    const data = await fetchJson(url);
    return data;
  };

  const cargarCursos = async () => {
    try {
      if (!selCurso) return;
      const res = await fetchJson('/administrador/cursos/lista');
      if (res.success && Array.isArray(res.cursos)) {
        selCurso.innerHTML = '<option value="">Seleccione...</option>' + res.cursos.map(c => {
          const nombre = c.nombre || `${c.grado || ''}${c.grupo || ''}`;
          return `<option value="${c.id}">${nombre}</option>`;
        }).join('');
        // Preseleccionar
        if (cursoId && res.cursos.some(c => String(c.id) === String(cursoId))) {
          selCurso.value = String(cursoId);
        } else if (cursoId && !res.cursos.some(c => String(c.id) === String(cursoId))) {
          // El curso puede estar inactivo o llegar como código 1101: agregamos opción temporal
          const opt = document.createElement('option');
          opt.value = String(cursoId);
          opt.textContent = String(cursoId);
          selCurso.appendChild(opt);
          selCurso.value = String(cursoId);
        } else if (res.cursos.length > 0) {
          selCurso.value = String(res.cursos[0].id);
        }
      }
    } catch (e) {
      console.error('Error cargando cursos', e);
    }
  };

  const renderTablaGrupo = (curso_label, est_count) => {
    const grado = curso_label ? String(curso_label).replace(/[^0-9A-Za-z]/g, '') : '';
    tablaGrupoBody.innerHTML = `
      <tr>
        <td>${grado.slice(0, -2)}</td>
        <td>${curso_label || ''}</td>
        <td>-</td>
        <td>${est_count ?? '-'}</td>
        <td>-</td>
        <td>-</td>
      </tr>`;
  };

  const renderGraficaAcademica = (rendimiento) => {
    const labels = rendimiento.map(r => r.asignatura);
    const dataVals = rendimiento.map(r => Number(r.promedio || 0));

    if (chartAcad) chartAcad.destroy();
    chartAcad = new Chart(ctxAcad, {
      type: 'bar',
      data: {
        labels,
        datasets: [{
          label: 'Promedio',
          data: dataVals,
          backgroundColor: '#050733ff',
          borderColor: '#1b2068',
          borderWidth: 1,
          hoverBackgroundColor: '#1b2068'
        }]
      },
      options: {
        scales: {
          y: { beginAtZero: true, max: 5, grid: { color: 'rgba(0,0,0,0.05)' } },
          x: { grid: { display: false } }
        },
        plugins: {
          tooltip: {
            callbacks: {
              label: (ctx) => {
                const val = Number(ctx.raw || 0);
                const pct = (val / 5) * 100;
                return ` ${val.toFixed(2)} (${pct.toFixed(0)}%)`;
              }
            }
          },
          legend: { display: false }
        }
      }
    });
  };

  const renderGraficaAsistencia = (asis) => {
    const labels = ['Presente', 'Ausente', 'Justificado'];
    const dataVals = [asis.Presente || 0, asis.Ausente || 0, asis.Justificado || 0];
    const total = Math.max(1, dataVals.reduce((a, b) => a + b, 0));

    if (chartAsis) chartAsis.destroy();
    chartAsis = new Chart(ctxAsis, {
      type: 'bar',
      data: {
        labels,
        datasets: [{
          label: 'Asistencia',
          data: dataVals,
          backgroundColor: ['#28a745', '#dc3545', '#ffc107'],
          borderColor: '#1b2068',
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: { beginAtZero: true, grid: { color: 'rgba(0,0,0,0.05)' } },
          x: { grid: { display: false } }
        },
        plugins: {
          tooltip: {
            callbacks: {
              label: (ctx) => {
                const val = Number(ctx.raw || 0);
                const pct = (val / total) * 100;
                return ` ${ctx.label}: ${val} (${pct.toFixed(0)}%)`;
              }
            }
          },
          legend: { display: false }
        }
      }
    });
  };

  const renderGraficaDisciplina = (serie) => {
    const labels = serie.map(s => `Ciclo ${s.periodo}`);
    const dataVals = serie.map(s => Number(s.observaciones || 0));
    const total = Math.max(1, dataVals.reduce((a, b) => a + b, 0));

    if (chartDisc) chartDisc.destroy();
    chartDisc = new Chart(ctxDisc, {
      type: 'bar',
      data: {
        labels,
        datasets: [{
          label: 'Conducta',
          data: dataVals,
          backgroundColor: '#050733ff',
          borderColor: '#1b2068',
          borderWidth: 1
        }]
      },
      options: {
        scales: { y: { beginAtZero: true, grid: { color: 'rgba(0,0,0,0.05)' } }, x: { grid: { display: false } } },
        plugins: {
          tooltip: {
            callbacks: {
              label: (ctx) => {
                const val = Number(ctx.raw || 0);
                const pct = (val / total) * 100;
                return ` ${val} reportes (${pct.toFixed(0)}%)`;
              }
            }
          },
          legend: { display: false }
        }
      }
    });
  };

  const renderEstudiantes = async () => {
    const selectedCurso = selCurso && selCurso.value ? selCurso.value : (cursoId || '');
    if (!selectedCurso) {
      tablaEstBody.innerHTML = '<tr><td colspan="6" class="text-center text-muted">Seleccione un curso.</td></tr>';
      return;
    }
    try {
      const periodo = selPeriodo.value || '';
      const url = `/administrador/informe/estudiantes?curso_id=${encodeURIComponent(selectedCurso)}${periodo ? `&periodo=${periodo}` : ''}`;
      const data = await fetchJson(url);
      if (!data.success) throw new Error(data.error || 'Error');
      if (!data.items || data.items.length === 0) {
        tablaEstBody.innerHTML = '<tr><td colspan="6" class="text-center text-muted">Sin estudiantes para mostrar.</td></tr>';
        return;
      }
      tablaEstBody.innerHTML = data.items.map((it, idx) => `
        <tr>
          <td>${it.id}</td>
          <td class="text-start">${it.nombre}</td>
          <td class="text-center">${it.asistencias}</td>
          <td class="text-center">${it.fallas}</td>
          <td class="text-center">${it.retardos}</td>
          <td class="text-center">${it.observaciones}</td>
        </tr>
      `).join('');
    } catch (e) {
      console.error('Error estudiantes:', e);
      tablaEstBody.innerHTML = '<tr><td colspan="6" class="text-center text-danger">Error al cargar estudiantes.</td></tr>';
    }
  };

  const actualizar = async () => {
    try {
      const data = await cargarDatos();
      if (!data || !data.success) throw new Error(data?.error || 'Error');
      renderTablaGrupo(data.curso_label, data.est_count);
      renderGraficaAcademica(data.rendimiento || []);
      renderGraficaAsistencia(data.asistencia || { Presente: 0, Ausente: 0, Justificado: 0 });
      renderGraficaDisciplina(data.disciplina || []);
      await renderEstudiantes();
    } catch (e) {
      console.error('Error informe:', e);
      tablaGrupoBody.innerHTML = '<tr><td colspan="6" class="text-center text-danger">No hay datos para este curso.</td></tr>';
      if (chartAcad) chartAcad.destroy();
      if (chartAsis) chartAsis.destroy();
      if (chartDisc) chartDisc.destroy();
    }
  };

  btnRefrescar.addEventListener('click', actualizar);
  if (selCurso) selCurso.addEventListener('change', actualizar);
  selPeriodo.addEventListener('change', actualizar);

  // Exportar PDF
  if (btnPDF) btnPDF.addEventListener('click', async () => {
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF('p','pt','a4');
    const title = 'Informe de Desempeños';
    doc.setFontSize(16);
    doc.text(title, 40, 40);
    // Exportar tabla estudiantes
    const table = document.getElementById('tablaEstudiantes');
    if (table) {
      const rows = [...table.querySelectorAll('tbody tr')].map(tr => [...tr.children].map(td => td.textContent.trim()));
      const headers = [...table.querySelectorAll('thead tr th')].map(th => th.textContent.trim());
      const startY = 70;
      doc.autoTable({ head: [headers], body: rows, startY });
    }
    doc.save('InformeCurso.pdf');
  });

  // Exportar Excel (CSV sencillo)
  if (btnExcel) btnExcel.addEventListener('click', async () => {
    const table = document.getElementById('tablaEstudiantes');
    const headers = [...table.querySelectorAll('thead tr th')].map(th => '"'+th.textContent.replaceAll('"','""')+'"').join(',');
    const rows = [...table.querySelectorAll('tbody tr')].map(tr => {
      return [...tr.children].map(td => '"'+td.textContent.replaceAll('"','""')+'"').join(',');
    });
    const csv = [headers, ...rows].join('\n');
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = 'InformeCurso.csv';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  });

  (async () => {
    // Cargar cursos primero si hay selector
    await cargarCursos();
    await actualizar();
  })();
});
