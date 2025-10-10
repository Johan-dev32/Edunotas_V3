from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from flask_mail import Message
from werkzeug.utils import secure_filename
from Controladores.models import db, Docente_Asignatura, Programacion, Asistencia, Detalle_Asistencia, Actividad, Actividad_Estudiante, Observacion, Notificacion
import os
from Controladores.models import (
    db, Usuario, Matricula, Asignatura, Cronograma_Actividades,
    Actividad, Actividad_Estudiante, Periodo
)
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
    return render_template('Docentes/Registrar_Tareas_Actividades2.html',  # 👈 corregido
                           curso_id=curso_id,
                           actividades=actividades)


@Docente_bp.route('/tareas_actividades3/<int:curso_id>/<int:actividad_id>')
def tareas_actividades3(curso_id, actividad_id):
    # Buscar la actividad correspondiente
    actividad = next((a for a in actividades if a["id"] == actividad_id), None)

    if not actividad:
        flash("No se encontró la actividad seleccionada.", "warning")
        return redirect(url_for('Docente.tareas_actividades', curso_id=curso_id))

    pdf_url = None
    if actividad.get("pdf_nombre"):
        pdf_url = url_for('static', filename=f'uploads/{actividad["pdf_nombre"]}')

    return render_template('Docentes/Registrar_Tareas_Actividades3.html',
                           curso_id=curso_id,
                           actividad_id=actividad_id,
                           titulo_actividad=actividad["titulo"],
                           descripcion_actividad=actividad["instrucciones"],
                           fecha_entrega=actividad["fecha"],
                           hora_entrega=actividad["hora"],
                           pdf_url=pdf_url)


    
actividades = []

# -------------------------------
# Mostrar lista de actividades
# -------------------------------
@Docente_bp.route('/tareas_actividades/<int:curso_id>')
def tareas_actividades(curso_id):
    return render_template('Docentes/Registrar_Tareas_Actividades2.html',  # 👈 corregido
                           curso_id=curso_id,
                           actividades=actividades)


# -------------------------------
# Crear nueva actividad
# -------------------------------
from werkzeug.utils import secure_filename
import os
from flask import request, redirect, url_for, render_template, flash

@Docente_bp.route('/crear_actividad/<int:curso_id>', methods=['GET', 'POST'])
def crear_actividad(curso_id):
    if request.method == 'POST':
        titulo = request.form.get('titulo')
        instrucciones = request.form.get('instrucciones')
        fecha = request.form.get('fecha')
        hora = request.form.get('hora')

        # Subir PDF
        pdf_file = request.files.get('pdfUpload')
        pdf_nombre = None
        if pdf_file and pdf_file.filename != '':
            upload_folder = os.path.join(os.getcwd(), 'static', 'uploads')
            os.makedirs(upload_folder, exist_ok=True)
            pdf_nombre = secure_filename(pdf_file.filename)
            pdf_path = os.path.join(upload_folder, pdf_nombre)
            pdf_file.save(pdf_path)
            print("✅ PDF guardado en:", pdf_path)
        else:
            print("⚠️ No se recibió PDF")

        # Crear la actividad
        nueva_actividad = {
            "id": len(actividades) + 1,
            "titulo": titulo,
            "instrucciones": instrucciones,
            "fecha": fecha,
            "hora": hora,
            "pdf_nombre": pdf_nombre
        }

        actividades.append(nueva_actividad)

        # Redirigir a detalles
        return redirect(url_for('Docente.tareas_actividades3',
                                curso_id=curso_id,
                                actividad_id=nueva_actividad["id"]))

    # GET: mostrar formulario
    return render_template('Docentes/Crear_Actividad.html',
                           curso_id=curso_id,
                           actividad_id=len(actividades) + 1)
    
@Docente_bp.route('/editar_actividad/<int:id_actividad>')
def editar_actividad(id_actividad):
    # Temporalmente solo muestra un mensaje o plantilla vacía
    return f"Editar actividad {id_actividad} (en construcción)"



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
    return render_template('Docentes/Observador.html')

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
@Docente_bp.route('/api/crear_actividad', methods=['POST'])
@login_required
def api_crear_actividad():
    try:
        payload = request.get_json() or {}
        titulo = payload.get('titulo', 'Actividad')
        tipo = payload.get('tipo', 'Taller')
        curso_id = payload.get('curso_id')

        # crear actividad SIN ID_Cronograma_Actividades
        nueva = Actividad(Titulo=titulo, Tipo=tipo, Fecha=None, Estado='Pendiente')
        db.session.add(nueva)
        db.session.flush()  # para obtener ID_Actividad antes del commit

        # enlazar con cronograma
        periodo = Periodo.query.filter_by(Anio=datetime.datetime.now().year).first()
        if not periodo:
            periodo = Periodo.query.first()
        if curso_id and periodo:
            cron = Cronograma_Actividades(
                ID_Curso=curso_id,
                ID_Periodo=periodo.ID_Periodo,
                ID_Actividad=nueva.ID_Actividad,
                FechaInicial=None,
                FechaFinal=None
            )
            db.session.add(cron)

        db.session.commit()
        return jsonify({'ID_Actividad': nueva.ID_Actividad})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

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


