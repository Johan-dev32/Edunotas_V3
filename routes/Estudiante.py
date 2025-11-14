from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime
from sqlalchemy import or_, text, func
from sqlalchemy.exc import IntegrityError
from Controladores.models import db, Matricula, Actividad, Curso, Periodo, Asignatura, Programacion, Actividad_Estudiante, Notificacion, Bloques, Usuario, Encuesta, Encuesta_Respuesta, Tutorias, Citaciones, Nota_Calificaciones, Observacion

import os

from decimal import Decimal
#Definir el Blueprint para el administardor
Estudiante_bp = Blueprint('Estudiante', __name__, url_prefix='/estudiante')


@Estudiante_bp.route('/paginainicio')
def paginainicio():
    return render_template('Estudiante/Paginainicio_Estudiante.html')


# ---------------- NOTIFICACIONES ESTUDIANTE----------------




@Estudiante_bp.route('/encuestas')
def encuestas_estudiante():
    return render_template("Estudiante/encuestas.html")

# Listar encuestas activas
@Estudiante_bp.route('/api/encuestas')
def api_encuestas():
    # 1. Verificar autenticación usando Flask-Login
    if not current_user.is_authenticated:
        return jsonify([])

    # 2. Obtener el ID del usuario directamente de Flask-Login
    usuario_id = current_user.ID_Usuario
    
    encuestas = Encuesta.query.filter_by(Activa=True).all()
    data = []
    for e in encuestas:
        # Se sigue usando usuario_id para el filtro de respuesta
        respondida = Encuesta_Respuesta.query.filter_by(ID_Encuesta=e.ID_Encuesta, ID_Usuario=usuario_id).first() is not None
        
        data.append({
            "id": e.ID_Encuesta,
            "titulo": e.Titulo,
            "descripcion": e.Descripcion,
            "respondida": respondida,
            "vencida": e.FechaCierre < datetime.utcnow() if e.FechaCierre else False
        })
    return jsonify(data)

# Obtener preguntas (No requiere cambios en la lógica de usuario)
@Estudiante_bp.route('/api/encuestas/<int:id_encuesta>')
def api_encuesta_detalle(id_encuesta):
    encuesta = Encuesta.query.get_or_404(id_encuesta)
    preguntas = []
    for p in encuesta.preguntas:
        preguntas.append({
            "ID_Pregunta": p.ID_Pregunta,
            "texto": p.TextoPregunta,
            "tipo": p.TipoRespuesta
        })
    return jsonify({
        "id": encuesta.ID_Encuesta,
        "titulo": encuesta.Titulo,
        "descripcion": encuesta.Descripcion,
        "preguntas": preguntas
    })

# Guardar respuestas (Lógica de autenticación, rol y matrícula)
@Estudiante_bp.route('/api/encuestas/<int:id_encuesta>/responder', methods=['POST'])
def responder_encuesta(id_encuesta):
    
    # 1. Verificar autenticación y obtener ID
    if not current_user.is_authenticated:
        return jsonify({"error": "No hay sesión activa"}), 403
    
    usuario_id = current_user.ID_Usuario
    
    # 2. Obtener usuario y verificar Rol
    usuario_check = Usuario.query.get(usuario_id) 
    if usuario_check.Rol != 'Estudiante':
        return jsonify({"error": "Permiso denegado: Rol no autorizado."}), 403

    # 3. Verificar si la encuesta caducó
    encuesta = Encuesta.query.get(id_encuesta)
    if encuesta.FechaCierre and encuesta.FechaCierre < datetime.utcnow():
        return jsonify({"error": "Esta encuesta ha caducado y no puede ser respondida."}), 409
    
    # 4. Usar el ID de la sesión para buscar la matrícula (Restricción)
    matricula_registro = Matricula.query.filter_by(ID_Estudiante=usuario_id).first()
    
    if not matricula_registro or not matricula_registro.ID_Matricula:
        return jsonify({"error": "Debe tener una matrícula activa para responder a esta encuesta."}), 403
    
    matricula_id = matricula_registro.ID_Matricula
    
    # 5. Prevenir doble envío
    if Encuesta_Respuesta.query.filter_by(ID_Encuesta=id_encuesta, ID_Usuario=usuario_id).first():
         return jsonify({"error": "Ya ha respondido esta encuesta."}), 409

    # 6. Guardar respuestas
    data = request.json
    respuestas = data.get("respuestas", {})
    
    for id_pregunta, respuesta_texto in respuestas.items():
        nueva_respuesta = Encuesta_Respuesta(
            ID_Pregunta=int(id_pregunta),
            ID_Usuario=usuario_id,
            ID_Encuesta=id_encuesta,
            ID_Matricula=matricula_id, 
            Respuesta=respuesta_texto
        )
        db.session.add(nueva_respuesta)
        
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        # Puedes usar un logger de Flask o un print temporal
        print(f"ERROR DE BASE DE DATOS AL GUARDAR RESPUESTA: {e}") 
        return jsonify({"error": "Error interno al guardar las respuestas. Intente de nuevo."}), 500
        
    return jsonify({"success": True})



@Estudiante_bp.route('/verhorario')
@login_required  # 
def verhorario():
    if current_user.Rol != 'Estudiante':
        return "Acceso no autorizado", 403

    estudiante = current_user  # ya es el usuario logueado

    # Obtener la matrícula más reciente del estudiante
    matricula = (
        Matricula.query
        .filter_by(ID_Estudiante=estudiante.ID_Usuario)
        .order_by(Matricula.AnioLectivo.desc())
        .first()
    )

    if not matricula:
        return "El estudiante no tiene una matrícula registrada", 404

    # Obtener el curso y las programaciones
    curso = matricula.curso
    programaciones = curso.programaciones.all() if curso else []

    return render_template(
        'Estudiante/VerHorario.html',
        estudiante=estudiante,
        curso=curso,
        programaciones=programaciones
    )

@Estudiante_bp.route('/api/curso/<int:curso_id>/horario')
def horario_estudiante(curso_id):
    bloques = Bloques.query.filter_by(curso_id=curso_id).all()
    resultado = []
    for b in bloques:
        resultado.append({
            "dia": b.dia,
            "hora_inicio": b.hora_inicio,
            "materia": b.materia,
            "docente": b.docente
        })
    return jsonify(resultado)


@Estudiante_bp.route('/vernotas')
def vernotas():
    return render_template('Estudiante/VerNotas.html')

@Estudiante_bp.route('/MaterialDidactico')
def MaterialDidactico():
    return render_template('Estudiante/MaterialDidactico.html')

@Estudiante_bp.route('/entregatareas')
def entregatareas():
    return render_template('Estudiante/EntregaTareas.html')

@Estudiante_bp.route('/entregatareas2')
def entregatareas2():
    return render_template('Estudiante/EntregaTareas2.html')

@Estudiante_bp.route('/entregatareas3')
def entregatareas3():
    return render_template('Estudiante/EntregaTareas3.html')

@Estudiante_bp.route('/evaluaciones')
def evaluaciones():
    return render_template('Estudiante/Evaluaciones.html')

                                                 
@Estudiante_bp.route('/tutorias')
def tutorias():
    return render_template('Estudiante/Tutorias.html')

@Estudiante_bp.route('/tutorias/historial', methods=['GET'])
@login_required
def tutorias_historial_estudiante():
    try:
        if current_user.Rol != 'Estudiante':
            return jsonify({"success": False, "error": "Acceso no autorizado"}), 403

        nombre_completo = f"{current_user.Nombre} {current_user.Apellido}".strip()
        correo = current_user.Correo

        # Filtrar tutorías dirigidas al estudiante por nombre o correo
        consulta = (
            Tutorias.query
            .filter(
                or_(
                    func.lower(Tutorias.NombreEstudiante) == func.lower(nombre_completo),
                    func.lower(Tutorias.Correo) == func.lower(correo)
                )
            )
            .order_by(Tutorias.FechaRealizacion.desc())
            .all()
        )

        result = [
            {
                "id": t.ID_Tutoria,
                "nombre": t.NombreCompleto,
                "rol": t.Rol,
                "tema": t.Tema,
                "fecha": t.FechaRealizacion.strftime("%Y-%m-%d") if t.FechaRealizacion else None,
                "curso": t.Curso,
                "estudiante": t.NombreEstudiante,
                "correo": t.Correo,
                "motivo": t.Motivo,
                "observaciones": t.Observaciones,
            }
            for t in consulta
        ]

        return jsonify({"success": True, "tutorias": result})
    except Exception as e:
        print(f"Error al cargar tutorías del estudiante: {e}")
        return jsonify({"success": False, "error": "Error de servidor"}), 500

@Estudiante_bp.route('/noticias')
def noticias():
    return render_template('Estudiante/Noticias.html')

@Estudiante_bp.route('/noticias_vistas')
def noticias_vistas():
    return render_template('Estudiante/Noticias_vistas.html')

@Estudiante_bp.route('/circulares_estudiantes')
def circulares_estudiantes():
    return render_template('Estudiante/CircularesEstudiantes.html')

@Estudiante_bp.route('/materias')
def materias():
    return render_template('Estudiante/Materias.html')

@Estudiante_bp.route('/tareas_actividades')
@login_required
def tareas_actividades():
    try:
        # Buscar las matrículas del estudiante actual
        matriculas = Matricula.query.filter_by(ID_Estudiante=current_user.ID_Usuario).all()
        cursos_ids = [m.ID_Curso for m in matriculas]

        # Buscar actividades relacionadas con sus cursos
        actividades = []
        if cursos_ids:
            actividades = Actividad.query.filter(Actividad.ID_Curso.in_(cursos_ids)).all()

        return render_template('Estudiante/TareasActividades.html', actividades=[(a, None) for a in actividades])
    except Exception as e:
        flash(f"Error al cargar actividades: {e}", "danger")
        return redirect(url_for('Estudiante.paginainicio'))
    
@Estudiante_bp.route('/subida_evidencias/<int:id_actividad>')
@login_required
def subida_evidencias(id_actividad):
    try:
        actividad = Actividad.query.get(id_actividad)
        if not actividad:
            flash("Actividad no encontrada.", "warning")
            return redirect(url_for('Estudiante.tareas_actividades'))

        return render_template('Estudiante/SubidaEvidencias.html',
                               actividad_id=actividad.ID_Actividad,
                               titulo_actividad=actividad.Titulo,
                               descripcion_actividad=actividad.Tipo,  # puedes reemplazar por otra descripción si la agregas
                               fecha_entrega=actividad.Fecha,
                               hora_entrega=None,
                               pdf_nombre=None)
    except Exception as e:
        flash(f"Error: {e}", "danger")
        return redirect(url_for('Estudiante.tareas_actividades'))
    
@Estudiante_bp.route('/enviar_evidencia/<int:id_actividad>', methods=['POST'])
@login_required
def enviar_evidencia(id_actividad):
    archivo = request.files.get('archivo')
    if not archivo:
        flash('Debes seleccionar un archivo.', 'warning')
        return redirect(url_for('Estudiante.subida_evidencias', id_actividad=id_actividad))
    
    upload_folder = os.path.join(os.getcwd(), 'static', 'uploads', 'evidencias')
    os.makedirs(upload_folder, exist_ok=True)
    filename = secure_filename(archivo.filename)
    archivo.save(os.path.join(upload_folder, filename))
    flash('Evidencia subida correctamente.', 'success')
    return redirect(url_for('Estudiante.tareas_actividades'))



@Estudiante_bp.route('/calculo_promedio')
def calculo_promedio():
    return render_template('Estudiante/CalculoPromedio.html')

@Estudiante_bp.route('/observador')
def observador():
    # ID del estudiante logueado (Asegúrate de que current_user esté disponible y tenga ID_Usuario)
    estudiante_id = current_user.ID_Usuario 

    # Consulta para obtener las observaciones del estudiante logueado
    observaciones = (
        db.session.query(Observacion, Usuario, Curso)
        .join(Matricula, Observacion.ID_Matricula == Matricula.ID_Matricula)
        .join(Usuario, Matricula.ID_Estudiante == Usuario.ID_Usuario)
        .join(Curso, Matricula.ID_Curso == Curso.ID_Curso)
        .filter(Matricula.ID_Estudiante == estudiante_id)
        .order_by(Observacion.Fecha.desc())
        .all()
    )

    return render_template(
        'Estudiante/Observador.html',
        observaciones=observaciones
    )


@Estudiante_bp.route('/observador/<int:anotacion_id>')
def observador_detalle(anotacion_id):
    estudiante_id = current_user.ID_Usuario 

    # Consulta para obtener una observación específica, asegurando que pertenezca al estudiante logueado
    anotacion = (
        db.session.query(Observacion, Usuario, Curso)
        .join(Matricula, Observacion.ID_Matricula == Matricula.ID_Matricula)
        .join(Usuario, Matricula.ID_Estudiante == Usuario.ID_Usuario)
        .join(Curso, Matricula.ID_Curso == Curso.ID_Curso)
        .filter(Observacion.ID_Observacion == anotacion_id, Matricula.ID_Estudiante == estudiante_id)
        .first()
    )

    if not anotacion:
        abort(404) # Si la anotación no existe o no pertenece al estudiante

    return render_template(
        'Estudiante/Observador2.html',
        anotacion=anotacion
    )

@Estudiante_bp.route('/aprobacion_academica')
def aprobacion_academica():
    return render_template('Estudiante/AprobacionAcademica.html')

@Estudiante_bp.route('/citaciones')
def citaciones():
    return render_template('Estudiante/Citaciones.html')

@Estudiante_bp.route('/citaciones2')
def citaciones2():
    return render_template('Estudiante/Citaciones2.html')

@Estudiante_bp.route('/citaciones/historial', methods=['GET'])
@login_required
def citaciones_historial_estudiante():
    try:
        # Permitimos acceso a cualquier usuario autenticado, siempre filtrando por su propia identidad

        correo = current_user.Correo
        uid = current_user.ID_Usuario
        override_id = request.args.get('estudiante_id', type=int)
        if override_id:
            uid = override_id

        consulta = (
            Citaciones.query
            .filter(
                or_(
                    Citaciones.ID_Usuario == uid,
                    func.lower(Citaciones.Correo) == func.lower(correo)
                )
            )
            .order_by(Citaciones.Fecha.desc())
            .all()
        )

        result = [
            {
                "id": c.ID_Citacion,
                "fecha": c.Fecha.strftime("%Y-%m-%d") if c.Fecha else None,
                "correo": c.Correo,
                "asunto": c.Asunto,
                "mensaje": c.RedaccionCitacion,
                "estado": c.Estado,
            }
            for c in consulta
        ]

        return jsonify({"success": True, "citaciones": result})
    except Exception as e:
        print(f"Error al cargar citaciones del estudiante: {e}")
        return jsonify({"success": False, "error": "Error de servidor"}), 500

@Estudiante_bp.route('/historial_academico')
def historial_academico():
    return render_template('Estudiante/HistorialAcademico.html')

@Estudiante_bp.route('/certificados')
def certificados():
    return render_template('Estudiante/Certificados.html')

@Estudiante_bp.route('/reportes_estudiante')
def reportes_estudiante():
    return render_template('Estudiante/ReportesEstudiante.html')

@Estudiante_bp.route('/manual')
def manual():
    return render_template('Estudiante/ManualUsuario.html')

#sub-vistas

@Estudiante_bp.route('/notas_curso')
def notas_curso():
    return render_template('Estudiante/NotasCurso.html')

@Estudiante_bp.route('/api/notas')
@login_required
def api_notas_estudiante():
    try:
        uid = current_user.ID_Usuario
        periodo = request.args.get('periodo', type=int)
        asignatura_id = request.args.get('asignatura', type=int)

        q = Nota_Calificaciones.query.filter_by(ID_Estudiante=uid)
        if periodo:
            q = q.filter(Nota_Calificaciones.Periodo == periodo)
        if asignatura_id:
            q = q.filter(Nota_Calificaciones.ID_Asignatura == asignatura_id)

        rows = q.all()
        data = []
        for r in rows:
            asig = Asignatura.query.get(r.ID_Asignatura)
            data.append({
                'ID_Calificacion': r.ID_Calificacion,
                'asignatura_id': r.ID_Asignatura,
                'asignatura': asig.Nombre if asig else None,
                'periodo': r.Periodo,
                'nota_1': r.Nota_1,
                'nota_2': r.Nota_2,
                'nota_3': r.Nota_3,
                'nota_4': r.Nota_4,
                'nota_5': r.Nota_5,
                'promedio': r.Promedio_Final,
            })

        return jsonify({'success': True, 'user_id': current_user.ID_Usuario, 'consulted_estudiante_id': uid, 'count': len(data), 'notas': data})
    except Exception as e:
        print(f"Error api_notas_estudiante: {e}")
        return jsonify({'success': False, 'error': 'Error de servidor'}), 500

@Estudiante_bp.route('/comunicacion')
def comunicacion():
    return render_template('Estudiante/Comunicacion.html')