from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from flask_mail import Message
from werkzeug.utils import secure_filename
from Controladores.models import ( db, Usuario, Matricula, Asignatura, Cronograma_Actividades, Actividad, Actividad_Estudiante, Periodo, Curso, Notificacion, Programacion, Observacion)
from datetime import date
import os

import datetime


from decimal import Decimal
#Definir el Blueprint para el administardor
Docente_bp = Blueprint('Docente', __name__, url_prefix='/docente')

@Docente_bp.route('/notificaciones', methods=['GET'])
@login_required
def obtener_notificaciones():
    notificaciones = Notificacion.query.filter_by(usuario_id=current_user.id).order_by(Notificacion.fecha.desc()).all()
    data = [
        {
            'titulo': n.titulo,
            'contenido': n.contenido,
            'fecha': n.fecha.strftime('%Y-%m-%d %H:%M:%S'),
            'leido': n.leido
        }
        for n in notificaciones
    ]
    return jsonify(data)

@Docente_bp.route('/paginainicio')
def paginainicio():
    return render_template('Docentes/Paginainicio_Docentes.html')

@Docente_bp.route('/manual')
def manual():
    return render_template('Docentes/ManualUsuario.html')

@Docente_bp.route('/materialapoyo')
def materialapoyo():
    return render_template('Docentes/MaterialApoyo.html')

@Docente_bp.route('/resumensemanal')
def resumensemanal():
    return render_template('Docentes/ResumenSemanal.html')

@Docente_bp.route('/registrotutorias')
def registrotutorias():
    return render_template('Docentes/RegistroTutorías.html')

@Docente_bp.route('/tareas_actividades1')
def tareas_actividades1():
    return render_template('Docentes/Registrar_Tareas_Actividades1.html')

@Docente_bp.route('/tareas_actividades2/<int:curso_id>')
def tareas_actividades2(curso_id):
    curso = Curso.query.get(curso_id)
    actividades = (Actividad.query
                   .join(Cronograma_Actividades)
                   .filter(Cronograma_Actividades.ID_Curso == curso_id)
                   .all())

    return render_template('Docentes/Registrar_Tareas_Actividades2.html',
                           curso=curso,
                           curso_id=curso_id,
                           actividades=actividades)


@Docente_bp.route('/tareas_actividades3/<int:curso_id>/<int:actividad_id>')
def tareas_actividades3(curso_id, actividad_id):
    # Buscar la actividad en la base de datos
    actividad = Actividad.query.get(actividad_id)

    if not actividad:
        flash("No se encontró la actividad seleccionada.", "warning")
        return redirect(url_for('Docente.tareas_actividades', curso_id=curso_id))

    # Obtener datos del cronograma (si existen)
    cronograma = actividad.cronograma

    # Preparar variables para enviar al HTML
    pdf_url = None
    if hasattr(actividad, 'ArchivoPDF') and actividad.ArchivoPDF:  # Si luego agregas un campo para el archivo
        pdf_url = url_for('static', filename=f'uploads/{actividad.ArchivoPDF}')

    return render_template('Docentes/Registrar_Tareas_Actividades3.html',
                           curso_id=curso_id,
                           actividad_id=actividad.ID_Actividad,
                           titulo_actividad=actividad.Titulo,
                           descripcion_actividad=getattr(actividad, 'Descripcion', None),  # si agregas ese campo
                           fecha_entrega=actividad.Fecha.strftime('%Y-%m-%d') if actividad.Fecha else None,
                           hora_entrega=getattr(actividad, 'Hora', None),
                           pdf_url=pdf_url)




# -------------------------------------------
# Mostrar lista de actividades
# -------------------------------------------
@Docente_bp.route('/tareas_actividades/<int:curso_id>')
@login_required
def tareas_actividades(curso_id):
    curso = Curso.query.get(curso_id)
    actividades = Actividad.query.filter_by(ID_Curso=curso_id).all()
    return render_template(
        'Docentes/Registrar_Tareas_Actividades2.html',
        curso=curso,
        actividades=actividades
    )


# -------------------------------------------
# Crear nueva actividad
# -------------------------------------------
@Docente_bp.route('/crear_actividad/<int:curso_id>', methods=['GET', 'POST'])
@login_required
def crear_actividad(curso_id):
    curso = Curso.query.get_or_404(curso_id) # Buscar el curso por su ID
    if request.method == 'POST':
        titulo = request.form.get('titulo')
        tipo = request.form.get('tipo')  # 👈 coincide con Enum del modelo
        fecha = request.form.get('fecha')
        estado = request.form.get('estado') or 'Pendiente'  # valor por defecto
        porcentaje = request.form.get('porcentaje')
        instrucciones = request.form.get('instrucciones')  # opcional si lo agregas a la tabla

        # Buscar el cronograma correspondiente
        cronograma = Cronograma_Actividades.query.filter_by(ID_Curso=curso_id).first()
        if not cronograma:
            flash("No se encontró el cronograma para este curso.", "warning")
            return redirect(url_for('Docente.tareas_actividades', curso_id=curso_id))

        # Procesar archivo PDF
        pdf_file = request.files.get('pdfUpload')
        pdf_nombre = None
        if pdf_file and pdf_file.filename != '':
            upload_folder = os.path.join(os.getcwd(), 'app', 'static', 'uploads')
            os.makedirs(upload_folder, exist_ok=True)
            pdf_nombre = secure_filename(pdf_file.filename)
            pdf_file.save(os.path.join(upload_folder, pdf_nombre))

        # Crear objeto Actividad
        nueva_actividad = Actividad(
            Titulo=titulo,
            Tipo=tipo,
            Fecha=fecha,
            ID_Cronograma_Actividades=cronograma.ID_Cronograma_Actividades,
            Estado=estado,
            Porcentaje=porcentaje
        )

        # (Si luego agregas un campo para instrucciones o PDF, puedes guardarlos también)
        if hasattr(Actividad, 'Descripcion'):
            nueva_actividad.Descripcion = instrucciones
        if hasattr(Actividad, 'ArchivoPDF'):
            nueva_actividad.ArchivoPDF = pdf_nombre

        # Guardar en BD
        db.session.add(nueva_actividad)
        db.session.commit()

        flash("Actividad registrada correctamente.", "success")
        return redirect(url_for('Docente.tareas_actividades', curso_id=curso_id))
    
    curso = Curso.query.get_or_404(curso_id)

    # GET → Mostrar formulario vacío
    return render_template('Docentes/Registrar_Tareas_Actividades2.html', curso=curso)
    
@Docente_bp.route('/editar_actividad/<int:id_actividad>', methods=['GET', 'POST'])
@login_required
def editar_actividad(id_actividad):
    actividad = Actividad.query.get_or_404(id_actividad)

    if request.method == 'POST':
        try:
            # Obtener valores del formulario
            actividad.Titulo = request.form.get('titulo')
            actividad.Tipo = request.form.get('tipo')
            actividad.Fecha = request.form.get('fecha')
            actividad.Estado = request.form.get('estado')
            actividad.Porcentaje = request.form.get('porcentaje')
            
            # Procesar archivo PDF nuevo si se sube
            pdf_file = request.files.get('pdfUpload')
            if pdf_file and pdf_file.filename != '':
                upload_folder = os.path.join(os.getcwd(), 'app', 'static', 'uploads')
                os.makedirs(upload_folder, exist_ok=True)
                pdf_nombre = secure_filename(pdf_file.filename)
                pdf_path = os.path.join(upload_folder, pdf_nombre)
                pdf_file.save(pdf_path)
                # Si tu modelo tiene un campo de archivo:
                if hasattr(actividad, 'ArchivoPDF'):
                    actividad.ArchivoPDF = pdf_nombre

            # Guardar cambios
            db.session.commit()
            flash("Actividad actualizada correctamente.", "success")

            # Redirigir al listado del curso correspondiente
            if actividad.cronograma and actividad.cronograma.curso:
                return redirect(url_for('Docente.tareas_actividades', curso_id=actividad.cronograma.curso.ID_Curso))
            else:
                return redirect(url_for('Docente.tareas_actividades', curso_id=1))  # fallback

        except Exception as e:
            db.session.rollback()
            flash(f"Error al actualizar la actividad: {e}", "danger")

    # GET → Mostrar formulario con datos actuales
    return render_template('Docentes/Editar_Actividad.html', actividad=actividad)



@Docente_bp.route('/aprobacion_academica')
def aprobacion_academica():
    return render_template('Docentes/AprobacionAcademica.html')

@Docente_bp.route('/historial_academico')
def historial_academico():
    return render_template('Docentes/HistorialAcademico.html')

@Docente_bp.route('/citaciones')
def citaciones():
    return render_template('Docentes/Citaciones.html')

@Docente_bp.route('/medioscomunicacion')
def medioscomunicacion():
    return render_template('Docentes/Medios_Comunicacion.html')

@Docente_bp.route('/reunion')
def reunion():
    return render_template('Docentes/Reunion.html')

@Docente_bp.route('/noticias')
def noticias():
    return render_template('Docentes/Noticias.html')

@Docente_bp.route('/noticias_vistas')
def noticias_vistas():
    return render_template('Docentes/NoticiasVistas.html')

@Docente_bp.route('/notas_curso/<int:curso_id>')
def notas_curso(curso_id):
    return render_template("Docentes/notas_curso.html", curso_id=curso_id)


@Docente_bp.route('/registro_notas/<int:curso_id>')
def registro_notas(curso_id):
    return render_template('Administrador/RegistroNotas.html', curso_id=curso_id)


@Docente_bp.route('/notas_registro')
def notas_registro():
    return render_template('Docentes/Notas_Registro.html')

@Docente_bp.route('/notas_consultar')
def notas_consultar():
    return render_template('Docentes/Notas_Consultar.html')

@Docente_bp.route('/calculo_promedio')
def calculo_promedio():
    return render_template('Docentes/CalculoPromedio.html')

@Docente_bp.route('/observador')
def observador():
    observaciones = (
        db.session.query(Observacion, Usuario)
        .join(Matricula, Observacion.ID_Matricula == Matricula.ID_Matricula)
        .join(Usuario, Matricula.ID_Estudiante == Usuario.ID_Usuario)
        .add_columns(
            Observacion.Fecha,
            Observacion.Descripcion,
            Observacion.Recomendacion,
            Observacion.Tipo,
            Observacion.NivelImportancia,
            Usuario.Nombre,
            Usuario.Apellido
        )
        .all()
    )

    matriculas = Matricula.query.all()
    return render_template('docentes/observador.html', observaciones=observaciones, matriculas=matriculas)


@Docente_bp.route('/agregar_observacion', methods=['POST'])
def agregar_observacion():
    try:
        id_matricula = request.form['id_matricula']
        descripcion = request.form['descripcion']
        tipo = request.form['tipo']
        nivel_importancia = request.form['nivel_importancia']
        recomendacion = request.form['recomendacion']

        nueva_observacion = Observacion(
            Fecha=date.today(),
            Descripcion=descripcion,
            Tipo=tipo,
            NivelImportancia=nivel_importancia,
            Recomendacion=recomendacion,
            Estado='Activa',
            ID_Horario=None,
            ID_Matricula=id_matricula
        )

        db.session.add(nueva_observacion)
        db.session.commit()
        flash('✅ Observación agregada correctamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error al agregar observación: {e}', 'danger')

    return redirect(url_for('docentes.observador'))

@Docente_bp.route('/horarios')
def horarios():
    return render_template('Docentes/Horarios.html')




# ----------------- SUB-PÁGINAS -----------------
@Docente_bp.route('/materialapoyo2')
def materialapoyo2():
    return render_template('Docentes/MaterialApoyo2.html')

@Docente_bp.route('/registrotutorias2')
def registrotutorias2():
    return render_template('Docentes/RegistroTutorías2.html')



#--------------------------------LO DE NOTAS-----------------------

@Docente_bp.route('/api/materias/<int:curso_id>')
@login_required
def api_materias(curso_id):
    try:
        # buscamos las programaciones del curso y desde ellas la asignatura
        progs = Programacion.query.filter_by(ID_Curso=curso_id).all()
        seen = set()
        materias = []
        for p in progs:
            da = p.docente_asignatura  # relación definida en modelos
            if da and da.ID_Asignatura:
                a = Asignatura.query.get(da.ID_Asignatura)
                if a and a.ID_Asignatura not in seen:
                    seen.add(a.ID_Asignatura)
                    materias.append({'ID_Asignatura': a.ID_Asignatura, 'Nombre': a.Nombre})
        return jsonify(materias)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@Docente_bp.route('/api/estudiantes/<int:curso_id>')
@login_required
def api_estudiantes(curso_id):
    try:
        matriculas = Matricula.query.filter_by(ID_Curso=curso_id).all()
        students = []
        for m in matriculas:
            u = Usuario.query.get(m.ID_Estudiante)
            if u:
                students.append({
                    'ID_Matricula': m.ID_Matricula,
                    'ID_Estudiante': u.ID_Usuario,
                    'Nombre': f"{u.Nombre} {u.Apellido}"
                })
        return jsonify(students)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --- ENDPOINT: obtener actividades + estudiantes + calificaciones para curso+asignatura
@Docente_bp.route('/api/notas/<int:curso_id>/<int:asignatura_id>')
@login_required
def api_notas_por_materia(curso_id, asignatura_id):
    try:
        # 1) obtener actividades del curso (vía cronograma)
        cronos = Cronograma_Actividades.query.filter_by(ID_Curso=curso_id).all()
        activity_ids = [c.ID_Actividad for c in cronos] if cronos else []

        activities = []
        if activity_ids:
            activities = Actividad.query.filter(Actividad.ID_Actividad.in_(activity_ids)).all()

        # 2) intentar filtrar por asignatura (si el título contiene el nombre de la asignatura)
        asign = Asignatura.query.get(asignatura_id)
        filtered_activities = []
        warning = None
        if asign:
            name = (asign.Nombre or "").lower()
            for act in activities:
                if name and name in ((act.Titulo or "").lower()):
                    filtered_activities.append(act)

        if not filtered_activities:
            # fallback: devolver todas las actividades del curso (porque no hay FK directa Actividad->Asignatura)
            filtered_activities = activities
            if not filtered_activities:
                warning = "No se encontraron actividades para este curso."
            else:
                warning = ("No existe una relación directa Actividad→Asignatura en la BD; "
                           "se devuelven todas las actividades del curso. "
                           "Recomendado: agregar ID_Asignatura a Actividad para precisión.")

        # 3) estudiantes matriculados
        matriculas = Matricula.query.filter_by(ID_Curso=curso_id).all()
        students = []
        for m in matriculas:
            u = Usuario.query.get(m.ID_Estudiante)
            if u:
                students.append({
                    'ID_Matricula': m.ID_Matricula,
                    'ID_Estudiante': u.ID_Usuario,
                    'Nombre': f"{u.Nombre} {u.Apellido}"
                })

        # 4) calificaciones existentes (Actividad_Estudiante) para las actividades filtradas
        act_ids = [a.ID_Actividad for a in filtered_activities]
        grades = []
        if act_ids:
            ae_rows = Actividad_Estudiante.query.filter(Actividad_Estudiante.ID_Actividad.in_(act_ids)).all()
            for r in ae_rows:
                grades.append({
                    'ID_Actividad_Estudiante': r.ID_Actividad_Estudiante,
                    'ID_Actividad': r.ID_Actividad,
                    'ID_Matricula': r.ID_Matricula,
                    'Calificacion': float(r.Calificacion) if r.Calificacion is not None else None
                })

        return jsonify({
            'activities': [{'ID_Actividad': a.ID_Actividad, 'Titulo': a.Titulo} for a in filtered_activities],
            'students': students,
            'grades': grades,
            'warning': warning
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# --- ENDPOINT: crear nueva actividad + cronograma (opcional para cuando agregues columna nueva)
@Docente_bp.route('/api/crear_actividad/<int:curso_id>', methods=['POST'], endpoint='api_crear_actividad')
@login_required
def api_crear_actividad(curso_id):
    if request.method == 'POST':
        titulo = request.form['titulo']
        instrucciones = request.form['instrucciones']
        fecha = request.form['fecha']
        hora = request.form['hora']
        archivo = request.files.get('pdfUpload')

        # Guardar PDF (si se envía)
        nombre_archivo = None
        if archivo and archivo.filename.endswith('.pdf'):
            nombre_archivo = secure_filename(archivo.filename)
            ruta = os.path.join(current_app.config['UPLOAD_FOLDER'], nombre_archivo)
            archivo.save(ruta)

        # Crear registro en la base de datos
        nueva_actividad = Actividad(
            Titulo=titulo,
            Descripcion=instrucciones,
            Fecha=fecha,
            Hora=hora,
            ArchivoPDF=nombre_archivo,
            ID_Curso=curso_id
        )
        db.session.add(nueva_actividad)
        db.session.commit()

        flash('Actividad creada correctamente ✅', 'success')
        return redirect(url_for('Docente.tareas_actividades1'))

    return render_template('Docente/Crear_Actividad.html', curso_id=curso_id)


@Docente_bp.route('/crear_actividad/<int:curso_id>', methods=['GET', 'POST'], endpoint='form_crear_actividad')
@login_required
def form_crear_actividad(curso_id):
    return render_template('Docentes/Crear_Actividad.html', curso_id=curso_id)

# --- ENDPOINT: guardar (insert/update) calificaciones desde el frontend
@Docente_bp.route('/api/guardar_notas', methods=['POST'])
@login_required
def api_guardar_notas():
    try:
        payload = request.get_json() or {}
        updates = payload.get('updates', [])  # lista de {actividad_id, matricula_id, calificacion}
        results = {'saved': 0, 'created': 0, 'errors': []}

        for u in updates:
            try:
                actividad_id = int(u.get('actividad_id'))
                matricula_id = int(u.get('matricula_id'))
                cal = u.get('calificacion')
                cal_val = None if cal in [None, ""] else float(cal)

                # --- Verificar existencia antes de insertar
                actividad = Actividad.query.get(actividad_id)
                matricula = Matricula.query.get(matricula_id)
                if not actividad or not matricula:
                    results['errors'].append({
                        'actividad_id': actividad_id,
                        'matricula_id': matricula_id,
                        'error': 'Actividad o matrícula no existe'
                    })
                    continue

                # --- Actualizar o crear registro
                row = Actividad_Estudiante.query.filter_by(
                    ID_Actividad=actividad_id, ID_Matricula=matricula_id
                ).first()
                if row:
                    row.Calificacion = cal_val
                    results['saved'] += 1
                else:
                    nueva = Actividad_Estudiante(
                        ID_Actividad=actividad_id,
                        ID_Matricula=matricula_id,
                        Observaciones='',
                        Calificacion=cal_val
                    )
                    db.session.add(nueva)
                    results['created'] += 1

            except Exception as row_error:
                results['errors'].append({
                    'actividad_id': u.get('actividad_id'),
                    'matricula_id': u.get('matricula_id'),
                    'error': str(row_error)
                })

        db.session.commit()
        return jsonify({'success': True, 'results': results})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# ----------------- ENVIAR CORREO CON ARCHIVO -----------------
@Docente_bp.route('/enviar_correo', methods=['GET', 'POST'])
@login_required
def enviar_correo():
    if request.method == 'POST':
        from app import mail 

        curso = request.form.get('curso')
        tipo = request.form.get('tipo')
        destinatario = request.form.get('correo')
        archivo = request.files.get('archivo')

        try:
            msg = Message(
                subject=f"{tipo} - Curso {curso}",
                recipients=[destinatario],
                body=f"Se envía el archivo correspondiente al curso {curso}."
            )

            if archivo:
                msg.attach(
                    archivo.filename,
                    archivo.content_type,
                    archivo.read()
                )

            mail.send(msg)
            flash("Correo enviado correctamente ✅", "success")
        except Exception as e:
            flash(f"Error al enviar: {e}", "danger")

        return redirect(url_for('Administrador.enviar_correo'))

    return render_template("Administrador/EnviarCorreo.html")


