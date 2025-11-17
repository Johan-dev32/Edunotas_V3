document.addEventListener("DOMContentLoaded", () => {
  const btnGuardar = document.getElementById("guardarPeriodos");
  const confirmBtn = document.getElementById("confirmGuardar");
  const modalEl = document.getElementById("confirmModal");

  // 👉 Solo ejecutar lógica de periodos si los elementos existen en la vista actual
  const p1i = document.getElementById("p1_inicio");
  if (p1i) {
    const datosGuardados = JSON.parse(localStorage.getItem("fechasPeriodos"));
    if (datosGuardados) {
      document.getElementById("p1_inicio").value = datosGuardados.p1.inicio;
      document.getElementById("p1_fin").value = datosGuardados.p1.fin;
      document.getElementById("p2_inicio").value = datosGuardados.p2.inicio;
      document.getElementById("p2_fin").value = datosGuardados.p2.fin;
      document.getElementById("p3_inicio").value = datosGuardados.p3.inicio;
      document.getElementById("p3_fin").value = datosGuardados.p3.fin;
      document.getElementById("p4_inicio").value = datosGuardados.p4.inicio;
      document.getElementById("p4_fin").value = datosGuardados.p4.fin;

      document.getElementById("resumen_p1").innerHTML = `<div class="mini-barra">Inicio ${datosGuardados.p1.inicio} - Fin ${datosGuardados.p1.fin}</div>`;
      document.getElementById("resumen_p2").innerHTML = `<div class="mini-barra">Inicio ${datosGuardados.p2.inicio} - Fin ${datosGuardados.p2.fin}</div>`;
      document.getElementById("resumen_p3").innerHTML = `<div class="mini-barra">Inicio ${datosGuardados.p3.inicio} - Fin ${datosGuardados.p3.fin}</div>`;
      document.getElementById("resumen_p4").innerHTML = `<div class="mini-barra">Inicio ${datosGuardados.p4.inicio} - Fin ${datosGuardados.p4.fin}</div>`;
    }

    if (btnGuardar) btnGuardar.addEventListener("click", () => {
      let inputs = document.querySelectorAll(".periodos-card input[type='date']");
      let incompletos = [];
      inputs.forEach((inp) => { if (!inp.value) incompletos.push(inp); });
      if (incompletos.length > 0) {
        alert("⚠️ No puedes guardar. Faltan fechas por completar.");
        return;
      }
      let modal = new bootstrap.Modal(modalEl);
      modal.show();
    });

    if (confirmBtn) confirmBtn.addEventListener("click", () => {
      let datos = {
        p1: { inicio: document.getElementById("p1_inicio").value, fin: document.getElementById("p1_fin").value },
        p2: { inicio: document.getElementById("p2_inicio").value, fin: document.getElementById("p2_fin").value },
        p3: { inicio: document.getElementById("p3_inicio").value, fin: document.getElementById("p3_fin").value },
        p4: { inicio: document.getElementById("p4_inicio").value, fin: document.getElementById("p4_fin").value },
      };
      localStorage.setItem("fechasPeriodos", JSON.stringify(datos));
      let modal = bootstrap.Modal.getInstance(modalEl);
      if (modal) modal.hide();
      document.getElementById("resumen_p1").innerHTML = `<div class=\"mini-barra\">Inicio ${datos.p1.inicio} - Fin ${datos.p1.fin}</div>`;
      document.getElementById("resumen_p2").innerHTML = `<div class=\"mini-barra\">Inicio ${datos.p2.inicio} - Fin ${datos.p2.fin}</div>`;
      document.getElementById("resumen_p3").innerHTML = `<div class=\"mini-barra\">Inicio ${datos.p3.inicio} - Fin ${datos.p3.fin}</div>`;
      document.getElementById("resumen_p4").innerHTML = `<div class=\"mini-barra\">Inicio ${datos.p4.inicio} - Fin ${datos.p4.fin}</div>`;
      alert("✅ Fechas de periodos guardadas correctamente");
    });
  }

  // -------- ConfiguracionAcademica3 (listar estudiantes reales) --------
  const selCurso = document.getElementById('curso');
  const selMateria = document.getElementById('materia');
  const tablaCont = document.querySelector('.tabla-container');
  const tabla = tablaCont ? tablaCont.querySelector('table') : null;
  const tbody = tabla ? tabla.querySelector('tbody') : null;

  const fetchJson = async (url) => {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  };

  const cargarTablaConfig3 = async () => {
    if (!tbody) return;
    // Obtener curso desde select o query param
    const params = new URLSearchParams(window.location.search);
    const cursoUrl = params.get('curso_id');
    const cursoVal = selCurso ? (selCurso.value || '').trim() : (cursoUrl || '').trim();
    if (!cursoVal) {
      tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted">Seleccione un curso.</td></tr>';
      return;
    }
    try {
      // Asignatura por id desde select o resolver por nombre desde query
      let asigVal = selMateria && selMateria.value && selMateria.value !== 'all' ? selMateria.value : '';
      const materiaNombre = params.get('materia');
      if (!asigVal && materiaNombre) {
        // Resolver id por nombre
        try {
          const resp = await fetchJson(`/administrador/asignaturas/lista?curso_id=${encodeURIComponent(cursoVal)}`);
          let asigns = resp.success ? (resp.asignaturas || []) : [];
          if (asigns.length === 0) {
            const respAll = await fetchJson('/administrador/asignaturas/lista');
            if (respAll.success) asigns = respAll.asignaturas || [];
          }
          const norm = (s) => (s || '').toString().trim().toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
          const target = norm(materiaNombre);
          let found = asigns.find(a => norm(a.nombre) === target);
          if (!found) {
            found = asigns.find(a => norm(a.nombre).includes(target) || target.includes(norm(a.nombre)));
          }
          if (found) asigVal = String(found.id);
        } catch (e) { console.warn('No se pudo resolver asignatura por nombre', e); }
      }
      const url = `/administrador/config3/datos?curso_id=${encodeURIComponent(cursoVal)}${asigVal ? `&asignatura_id=${encodeURIComponent(asigVal)}` : ''}`;
      const data = await fetchJson(url);
      if (!data.success) throw new Error(data.error || 'Error');
      if (!data.items || data.items.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted">Sin datos para este curso.</td></tr>';
        return;
      }
      tbody.innerHTML = data.items.map(it => `
        <tr>
          <td>${it.detalles}</td>
          <td>${it.nombre}</td>
          <td>${it.documento || ''}</td>
          <td>${it.promedio != null ? it.promedio.toFixed(2) : '-'}</td>
          <td>${it.nivel}</td>
          <td>${it.observacion}</td>
          <td>${it.periodo || ''}</td>
        </tr>
      `).join('');
    } catch (e) {
      console.error('Config3 datos error:', e);
      tbody.innerHTML = '<tr><td colspan="7" class="text-center text-danger">Error al cargar datos.</td></tr>';
    }
  };

  const cargarMaterias = async () => {
    if (!selMateria || !selCurso) return;
    const cursoVal = (selCurso.value || '').trim();
    try {
      const resp = await fetchJson(`/administrador/asignaturas/lista?curso_id=${encodeURIComponent(cursoVal)}`);
      if (!resp.success) throw new Error(resp.error || 'Error');
      let asigns = resp.asignaturas || [];
      // Fallback: si el curso no retorna materias, carga todas sin filtrar
      if (asigns.length === 0) {
        const respAll = await fetchJson('/administrador/asignaturas/lista');
        if (respAll.success && Array.isArray(respAll.asignaturas)) {
          asigns = respAll.asignaturas;
        }
      }
      const opts = ['<option value="all">Todas</option>']
        .concat(asigns.map(a => `<option value="${a.id}">${a.nombre}</option>`));
      selMateria.innerHTML = opts.join('');
      // Selección por defecto: 'Todas' o primera asignatura
      selMateria.value = 'all';
      if (asigns.length > 0 && !selMateria.value) {
        selMateria.value = String(asigns[0].id);
      }
    } catch (e) {
      console.error('Error cargando asignaturas:', e);
      // fallback simple si falla
      selMateria.innerHTML = '<option value="all">Todas</option>';
      selMateria.value = 'all';
    }
  };

  if (selCurso && tbody) {
    selCurso.addEventListener('change', async () => {
      await cargarMaterias();
      await cargarTablaConfig3();
    });
    if (selMateria) selMateria.addEventListener('change', cargarTablaConfig3);
    // Autoselección por query param ?curso_id=XXXX
    const params = new URLSearchParams(window.location.search);
    const qCurso = params.get('curso_id');
    const qMateriaNombre = params.get('materia');
    if (qCurso) {
      // Si el valor existe en el select, seleccionarlo
      const opt = [...selCurso.options].find(o => String(o.value) === String(qCurso));
      if (opt) selCurso.value = qCurso;
    }
    // Cargar al iniciar
    (async () => {
      await cargarMaterias();
      // Si viene materia por nombre, seleccionarla por coincidencia de texto
      if (qMateriaNombre && selMateria && selMateria.options.length > 0) {
        const target = qMateriaNombre.trim().toLowerCase();
        const match = [...selMateria.options].find(o => (o.textContent || '').trim().toLowerCase() === target);
        if (match) selMateria.value = match.value;
        // Ocultar filtros si deep-link activo
        const header = document.querySelector('.tabla-container > .d-flex');
        if (header) header.classList.add('d-none');
      }
      await cargarTablaConfig3();
    })();
  }

  // Modo sin filtros: cargar directo por query params
  if (!selCurso && tbody) {
    (async () => {
      // Ocultar cabecera de acciones si existe
      const header = document.querySelector('.tabla-container > .d-flex');
      if (header) header.classList.add('d-none');
      await cargarTablaConfig3();
    })();
  }
});
