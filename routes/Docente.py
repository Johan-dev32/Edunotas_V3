from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session, current_app, send_from_directory, make_response
from flask_login import login_required, current_user
from flask_mail import Message
from werkzeug.utils import secure_filename
import io
from xhtml2pdf import pisa
from Controladores.models import ( db, Usuario, Matricula, Asignatura, Cronograma_Actividades, Actividad, Actividad_Estudiante, Periodo, Curso, Notificacion, Programacion, Observacion, Nota_Calificaciones, Docente_Asignatura, ResumenSemanal, Tutorias, Acudiente, MaterialDidactico, Asistencia, Detalle_Asistencia, Historial_Academico )
from sqlalchemy import text
from sqlalchemy.orm import aliased
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from datetime import date, datetime
import os




from decimal import Decimal


#Definir el Blueprint para el administardor
Docente_bp = Blueprint('Docente', __name__, url_prefix='/docente')
ID_DOCENTE_FIJO = 2




@Docente_bp.route('/paginainicio')
def paginainicio():
    return render_template('Docentes/Paginainicio_Docentes.html')



# ---------------- NOTIFICACIONES DOCENTE----------------




@Docente_bp.route('/manual')
def manual():
    return render_template('Docentes/ManualUsuario.html')



@Docente_bp.route('/resumensemanal')
def resumensemanal():
    return render_template('Docentes/ResumenSemanal.html')

@Docente_bp.route('/resumensemanal/registro', methods=['POST'])
def registrar_resumen_semanal():
    try:
        # 1. Obtener datos del formulario
        # Nota: Los nombres deben coincidir con los atributos 'name' del HTML
        fecha_str = request.form.get('fecha')
        titulo = request.form.get('titulo')
        actividades = request.form.get('redaccion')
        
        # 2. Obtener el ID del usuario logueado (CRÍTICO)
        # DEBES ASEGURARTE DE QUE ESTA VARIABLE FUNCIONE EN TU APLICACIÓN
        # Si no usas session, usa el método que tengas para obtener el ID del usuario logueado.
        creado_por_id = session.get('user_id', 1) # Usamos 1 como fallback si la sesión no está lista

        if not fecha_str or not titulo or not actividades:
            return jsonify({'success': False, 'error': 'Faltan campos obligatorios.'}), 400

        # Convertir fecha de string a datetime si es necesario, o solo usar el string si la DB lo acepta
        # Lo mejor es convertirlo:
        from datetime import datetime
        fecha_dt = datetime.strptime(fecha_str, '%Y-%m-%d')
        
        # 3. Crear y guardar el nuevo objeto ResumenSemanal
        nuevo_resumen = ResumenSemanal(
            Fecha=fecha_dt,
            CreadoPor=creado_por_id,
            Titulo=titulo,
            ActividadesRealizadas=actividades
        )
        
        db.session.add(nuevo_resumen)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Resumen guardado exitosamente.'})

    except Exception as e:
        db.session.rollback()
        print(f"Error al registrar resumen: {e}")
        # Retornamos 500 para indicar un fallo interno del servidor
        return jsonify({'success': False, 'error': f'Error interno del servidor: {str(e)}'}), 500

@Docente_bp.route('/registrotutorias')
def registrotutorias():
    return render_template('Docentes/RegistroTutorías.html')




# ----------------------------------------------------------------------------------------
#---------------------------------parte de actividades----------------------------
# -------------------------------------------------------------------------------

@Docente_bp.route("/tutorias/historial", methods=["GET"])
def historial_tutorias():
    """
    Ruta API para cargar todas las tutorías guardadas en la BD.
    Esta es la ruta que llama el JavaScript al cargar la página.
    """
    try:
        # Consulta las tutorías ordenadas por fecha de realización descendente (más recientes primero)
        tutorias = Tutorias.query.order_by(Tutorias.FechaRealizacion.desc()).all()
        
        result = [
            {
                "id": t.ID_Tutoria,
                "nombre": t.NombreCompleto,
                "rol": t.Rol,
                "tema": t.Tema,
                "fecha": t.FechaRealizacion.strftime("%Y-%m-%d"), 
                "curso": t.Curso, 
                "estudiante": t.NombreEstudiante, 
                "correo": t.Correo,
                "motivo": t.Motivo,
                "observaciones": t.Observaciones
            }
            for t in tutorias
        ]
        
        # Devuelve el JSON que el frontend espera
        return jsonify({"success": True, "tutorias": result})
        
    except Exception as e:
        print(f"Error al cargar historial de tutorías: {e}")
        return jsonify({"success": False, "error": "Error de servidor al cargar datos."}), 500
    
@Docente_bp.route("/tutorias/registro", methods=["POST"])
def guardar_tutoria():
    """
    Recibe los datos de la tutoría desde el modal y los guarda en la BD.
    """
    data = request.get_json()
    
    # 🚨 Validación de datos básicos
    if not all(key in data for key in ["nombre", "rol", "tema", "fecha", "curso", "estudiante", "correo", "motivo", "observaciones"]):
        return jsonify({"success": False, "error": "Faltan campos obligatorios."}), 400

    try:
        # Convertir la fecha de String ("YYYY-MM-DD") a objeto datetime
        fecha_realizacion = datetime.strptime(data["fecha"], "%Y-%m-%d")
        
        # Crear el nuevo objeto Tutorias (Alineado con el modelo modificado)
        nueva_tutoria = Tutorias(
            NombreCompleto=data["nombre"],
            Rol=data["rol"],
            Tema=data["tema"],
            FechaRealizacion=fecha_realizacion,
            Curso=data["curso"],                  
            NombreEstudiante=data["estudiante"],  
            Correo=data["correo"],
            Motivo=data["motivo"],
            Observaciones=data["observaciones"]
        )
        
        db.session.add(nueva_tutoria)
        db.session.commit()
        
        # Devolver el objeto guardado para que el JS actualice la tabla
        return jsonify({
            "success": True,
            "message": "Tutoría registrada con éxito.",
            "tutoria": {
                "id": nueva_tutoria.ID_Tutoria,
                "nombre": nueva_tutoria.NombreCompleto,
                "rol": nueva_tutoria.Rol,
                "tema": nueva_tutoria.Tema,
                "fecha": nueva_tutoria.FechaRealizacion.strftime("%Y-%m-%d"), 
                "curso": nueva_tutoria.Curso,
                "estudiante": nueva_tutoria.NombreEstudiante,
                "correo": nueva_tutoria.Correo,
                "motivo": nueva_tutoria.Motivo,
                "observaciones": nueva_tutoria.Observaciones
            }
        }), 201 
        
    except Exception as e:
        db.session.rollback()
        print(f"Error crítico al guardar tutoría en BD: {e}") 
        return jsonify({"success": False, "error": f"Error interno del servidor: {str(e)}", "trace": str(e)}), 500


@Docente_bp.route('/tareas_actividades1')
@login_required
def tareas_actividades1():
    # Obtener el ID del docente logueado
    docente_id = current_user.ID_Usuario
    print("Docente ID en sesión:", docente_id)

    # Buscar cursos donde ese docente tiene asignaciones
    cursos_asignados = (
        db.session.query(Curso)
        .join(Docente_Asignatura)
        .filter(Docente_Asignatura.ID_Docente == docente_id)
        .filter(Curso.Estado == 'Activo')
        .distinct()
        .all()
        
    )
    print("Cursos asignados:", [c.Grupo for c in cursos_asignados])
    # Clasificar por ciclo
    ciclos = {1: [], 2: [], 3: []}
    for c in cursos_asignados:
        grado = int(c.Grado)
        if grado in (6, 7):
            ciclos[1].append(c)
        elif grado in (8, 9):
            ciclos[2].append(c)
        elif grado in (10, 11):
            ciclos[3].append(c)
            
    

    return render_template('Docentes/Registrar_Tareas_Actividades1.html', ciclos=ciclos)
    
@Docente_bp.route('/tareas_actividades3/<int:curso_id>/<int:id_actividad>')
def tareas_actividades3(curso_id, id_actividad):
    # Buscar la actividad en la base de datos
    actividad = Actividad.query.get(id_actividad)

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
                           id_actividad=actividad.ID_Actividad,
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
    curso = Curso.query.get_or_404(curso_id)

    # Unir Actividad con Cronograma_Actividades para obtener las del curso
    actividades = (
        db.session.query(Actividad)
        .join(Cronograma_Actividades)
        .filter(Cronograma_Actividades.ID_Curso == curso_id)
        .all()
    )

    return render_template(
        'Docentes/Registrar_Tareas_Actividades2.html',
        curso=curso,
        actividades=actividades,
        curso_id=curso_id  # 👈 Esto es lo que faltaba
    )
# -------------------------------------------
# Crear nueva actividad
# -------------------------------------------

@Docente_bp.route('/crear_actividad/<int:curso_id>', methods=['GET', 'POST'])
@login_required
def crear_actividad(curso_id):

    relacion = Docente_Asignatura.query.filter_by(
        ID_Docente=current_user.ID_Usuario,
        ID_Curso=curso_id
    ).first()

    if not relacion:
        flash("No tienes una asignatura asociada a este curso.", "warning")
        return redirect(url_for('Docente.tareas_actividades1'))

    id_asignatura = relacion.ID_Asignatura

    if request.method == 'POST':
        try:
            titulo = request.form.get('titulo')
            descripcion = request.form.get('instrucciones')
            tipo = request.form.get('tipo')
            estado = request.form.get('estado', 'Pendiente')
            porcentaje = request.form.get('porcentaje')
            fecha = request.form.get('fecha')
            hora = request.form.get('hora')
            pdf = request.files.get('pdfUpload')

            print("ASIGNATURA RECIBIDA FORM:", request.form.get('id_asignatura'))

            if not all([titulo, descripcion, tipo, fecha, hora, porcentaje]):
                flash("Por favor completa todos los campos obligatorios.", "warning")
                return redirect(request.url)

            # Buscar o crear cronograma por curso **y asignatura**
            cronograma = Cronograma_Actividades.query.filter_by(
                ID_Curso=curso_id,
                ID_Asignatura=id_asignatura
            ).first()

            if not cronograma:
                cronograma = Cronograma_Actividades(
                    ID_Curso=curso_id,
                    ID_Periodo=1,
                    FechaInicial=datetime.now().date(),
                    FechaFinal=datetime.now().date(),
                    ID_Asignatura=id_asignatura
                )
                db.session.add(cronograma)
                db.session.commit()

            # Guardar PDF
            nombre_pdf = None
            if pdf and pdf.filename:
                nombre_seguro = secure_filename(pdf.filename)
                nombre_pdf = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{nombre_seguro}"
                ruta_pdf = os.path.join(current_app.config['UPLOAD_FOLDER'], nombre_pdf)
                pdf.save(ruta_pdf)

            # Crear actividad
            nueva_actividad = Actividad(
                Titulo=titulo,
                Tipo=tipo,
                Fecha=datetime.strptime(fecha, "%Y-%m-%d").date(),
                Hora=datetime.strptime(hora, "%H:%M").time(),
                Descripcion=descripcion,
                ArchivoPDF=nombre_pdf,
                Estado=estado,
                Porcentaje=porcentaje,
                ID_Cronograma_Actividades=cronograma.ID_Cronograma_Actividades
            )

            db.session.add(nueva_actividad)
            db.session.commit()

            flash("✅ Actividad publicada correctamente.", "success")
            return redirect(url_for('Docente.tareas_actividades', curso_id=curso_id))

        except Exception as e:
            db.session.rollback()
            print("❌ Error al crear actividad:", e)
            flash("Ocurrió un error al crear la actividad.", "danger")
            return redirect(request.url)

    # ========== SI ES GET → Renderizar HTML ==========
    return render_template(
        "Docentes/Crear_Actividad.html",
        curso_id=curso_id,
        id_asignatura=id_asignatura
    )
    
@Docente_bp.route('/editar_actividad/<int:id_actividad>', methods=['POST', 'GET'])
@login_required
def editar_actividad(id_actividad):
    actividad = Actividad.query.get_or_404(id_actividad)

    if request.method == 'POST':
        try:
            # Campos del form
            actividad.Titulo = request.form.get('titulo')
            actividad.Descripcion = request.form.get('descripcion')

            # Tipo (enum) y porcentaje
            tipo = request.form.get('tipo')
            if tipo:
                actividad.Tipo = tipo

            porcentaje = request.form.get('porcentaje')
            if porcentaje:
                try:
                    actividad.Porcentaje = float(porcentaje)
                except ValueError:
                    actividad.Porcentaje = actividad.Porcentaje  # no actualizar si mal

            # Fecha y hora
            fecha = request.form.get('fecha_entrega')
            hora = request.form.get('hora_entrega')

            if fecha:
                actividad.Fecha = datetime.strptime(fecha, "%Y-%m-%d").date()

            if hora:
                actividad.Hora = datetime.strptime(hora, "%H:%M").time()

            # Estado
            estado = request.form.get('estado')
            if estado:
                actividad.Estado = estado

            # Manejo de PDF: mantener si no subes uno nuevo, reemplazar si subes
            pdf_file = request.files.get('pdfUpload')
            if pdf_file and pdf_file.filename:
                pdf_seguro = secure_filename(pdf_file.filename)
                nuevo_nombre = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{pdf_seguro}"

                folder = current_app.config.get('UPLOAD_FOLDER')
                if not folder:
                    folder = os.path.join(current_app.root_path, 'static', 'uploads')
                    os.makedirs(folder, exist_ok=True)

                pdf_path = os.path.join(folder, nuevo_nombre)
                pdf_file.save(pdf_path)

                # opcional: eliminar archivo antiguo para no acumular (comenta si no quieres borrar)
                try:
                    if actividad.ArchivoPDF:
                        antiguo = os.path.join(folder, actividad.ArchivoPDF)
                        if os.path.exists(antiguo):
                            os.remove(antiguo)
                except Exception as e:
                    print("No se pudo eliminar antiguo PDF:", e)

                actividad.ArchivoPDF = nuevo_nombre

            db.session.commit()
            flash("Actividad actualizada correctamente.", "success")
            return redirect(url_for('Docente.tareas_actividades', curso_id=actividad.cronograma.ID_Curso))

        except Exception as e:
            db.session.rollback()
            print("Error al actualizar actividad:", e)
            flash(f"Error al actualizar la actividad: {e}", "danger")

    # GET -> render con objeto actividad
    return render_template('Docentes/Editar_Actividad.html', actividad=actividad)



@Docente_bp.route('/ver_pdf/<path:filename>')
@login_required
def ver_pdf(filename):
    """
    Permite ver o descargar el PDF de una actividad directamente desde /uploads.
    """
    upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
    
    try:
        return send_from_directory(upload_folder, filename, as_attachment=False)
    except FileNotFoundError:
        flash("❌ El archivo PDF no fue encontrado.", "danger")
        return redirect(url_for('Docente.tareas_actividades1'))
    


@Docente_bp.route('/ver_entregas')
@login_required
def ver_entregas_lista():
    try:
        # obtener asignaturas del docente
        asignaturas_docente = Docente_Asignatura.query.filter_by(
            ID_Docente=current_user.ID_Usuario
        ).all()

        id_asignaturas = [a.ID_Asignatura for a in asignaturas_docente]

        # obtener cronogramas ligados a esas asignaturas
        cronogramas = Cronograma_Actividades.query.filter(
            Cronograma_Actividades.ID_Asignatura.in_(id_asignaturas)
        ).all()

        id_cronogramas = [c.ID_Cronograma_Actividades for c in cronogramas]

        # obtener actividades de esos cronogramas
        actividades = Actividad.query.filter(
            Actividad.ID_Cronograma_Actividades.in_(id_cronogramas)
        ).all()

        return render_template(
            "Docentes/VerEntregasLista.html",
            actividades=actividades
        )

    except Exception as e:
        print("ERROR en ver_entregas_lista:", e)
        return render_template("Docentes/VerEntregasLista.html", actividades=[])


@Docente_bp.route('/entregas/<int:id_actividad>')
@login_required
def ver_entregas(id_actividad):

    if current_user.Rol != 'Docente':
        flash("Acceso no autorizado", "warning")
        return redirect(url_for('Docente.paginainicio'))

    actividad = Actividad.query.get(id_actividad)

    entregas = Actividad_Estudiante.query.filter_by(
        ID_Actividad=id_actividad
    ).all()

    return render_template(
        "Docentes/VerEntregas.html",
        actividad=actividad,
        entregas=entregas
    )
#----------------------------------------------------------------------------------------------------------------------------

@Docente_bp.route('/asistencia', methods=['GET', 'POST'])
@login_required
def asistencia():
    docente_id = current_user.ID_Usuario

    # Cursos disponibles para pasar asistencia
    # Por ahora cargamos todos los cursos activos, sin filtrar por Docente_Asignatura,
    # para que el combo siempre tenga opciones aunque aún no se haya configurado esa tabla.
    cursos = (
        Curso.query
        .filter_by(Estado='Activo')
        .order_by(Curso.Grado, Curso.Grupo)
        .all()
    )

    if not cursos:
        flash("No tiene cursos asignados para pasar asistencia.", "warning")
        return render_template('Docentes/Asistencia.html', cursos=[], curso_seleccionado=None, estudiantes=[])

    # Curso seleccionado (por querystring o por POST)
    if request.method == 'POST':
        curso_id = request.form.get('curso_id', type=int)
    else:
        curso_id = request.args.get('curso_id', type=int)

    if not curso_id:
        curso_id = cursos[0].ID_Curso

    curso_seleccionado = Curso.query.get(curso_id)

    # Estudiantes matriculados en el curso
    estudiantes = (
        db.session.query(Usuario)
        .join(Matricula, Matricula.ID_Estudiante == Usuario.ID_Usuario)
        .filter(Matricula.ID_Curso == curso_id, Usuario.Rol == 'Estudiante')
        .order_by(Usuario.Apellido, Usuario.Nombre)
        .all()
    )

    # Estados previos de asistencia (último registro por estudiante en este curso)
    from sqlalchemy import desc
    estados_previos = {}
    if estudiantes:
        detalles = (
            db.session.query(Detalle_Asistencia)
            .join(Asistencia, Detalle_Asistencia.ID_Asistencia == Asistencia.ID_Asistencia)
            .join(Programacion, Asistencia.ID_Programacion == Programacion.ID_Programacion)
            .filter(Programacion.ID_Curso == curso_id)
            .order_by(Asistencia.Fecha.desc(), Detalle_Asistencia.ID_Detalle_Asistencia.desc())
            .all()
        )

        for det in detalles:
            if det.ID_Estudiante not in estados_previos:
                estados_previos[det.ID_Estudiante] = det.Estado_Asistencia

    if request.method == 'POST':
        try:
            from datetime import date

            print("[DEBUG asistencia] POST recibido - docente_id=", docente_id, "curso_id=", curso_id)

            # Asegurar que exista una relación Docente_Asignatura para este curso y docente
            da = Docente_Asignatura.query.filter_by(ID_Docente=docente_id, ID_Curso=curso_id).first()
            if not da:
                # Tomar alguna asignatura existente (por ejemplo la primera activa)
                asig_ref = Asignatura.query.filter_by(Estado='Activa').order_by(Asignatura.ID_Asignatura).first()
                if not asig_ref:
                    raise Exception("No hay asignaturas activas para asociar a la asistencia.")

                da = Docente_Asignatura(
                    ID_Docente=docente_id,
                    ID_Asignatura=asig_ref.ID_Asignatura,
                    ID_Curso=curso_id
                )
                db.session.add(da)
                db.session.flush()
                print("[DEBUG asistencia] Docente_Asignatura creado con ID=", da.ID_Docente_Asignatura)

            # Buscar o crear una programación básica para este curso y docente/asignatura
            programacion = Programacion.query.filter_by(ID_Curso=curso_id, ID_Docente_Asignatura=da.ID_Docente_Asignatura).first()
            print("[DEBUG asistencia] Programacion existente:", bool(programacion))
            if not programacion:
                programacion = Programacion(
                    ID_Curso=curso_id,
                    ID_Docente_Asignatura=da.ID_Docente_Asignatura,
                    ID_Docente=docente_id,
                    Dia='N/A'
                )
                db.session.add(programacion)
                db.session.flush()
                print("[DEBUG asistencia] Programacion creada con ID=", programacion.ID_Programacion)

            asistencia_reg = Asistencia(
                Fecha=date.today(),
                ID_Programacion=programacion.ID_Programacion,
            )
            db.session.add(asistencia_reg)
            db.session.flush()  # para obtener ID_Asistencia
            print("[DEBUG asistencia] Asistencia creada con ID=", asistencia_reg.ID_Asistencia)

            # Recorrer estudiantes y guardar detalle de asistencia
            for est in estudiantes:
                estado = request.form.get(f"estado_{est.ID_Usuario}", 'Presente')
                print(f"[DEBUG asistencia] Estudiante {est.ID_Usuario} estado=", estado)

                detalle = Detalle_Asistencia(
                    ID_Asistencia=asistencia_reg.ID_Asistencia,
                    ID_Estudiante=est.ID_Usuario,
                    Estado_Asistencia=estado,
                )
                db.session.add(detalle)

                # Si es ausente, notificar al acudiente asociado
                if estado == 'Ausente':
                    relaciones = Acudiente.query.filter_by(ID_Estudiante=est.ID_Usuario, Estado='Activo').all()
                    materia_nombre = None
                    if programacion and programacion.docente_asignatura and programacion.docente_asignatura.asignatura:
                        materia_nombre = programacion.docente_asignatura.asignatura.Nombre

                    for rel in relaciones:
                        mensaje = f"El estudiante {est.Nombre} {est.Apellido} estuvo ausente el {asistencia_reg.Fecha.strftime('%d/%m/%Y')}"
                        if materia_nombre:
                            mensaje += f" en la asignatura {materia_nombre}."

                        notif = Notificacion(
                            Titulo="Registro de inasistencia",
                            Mensaje=mensaje,
                            Enlace=url_for('Acudiente.inasistencias_justificadas'),
                            ID_Usuario=rel.ID_Usuario,
                        )
                        db.session.add(notif)

            db.session.commit()
            print("[DEBUG asistencia] Commit realizado correctamente")
            flash("Asistencia registrada correctamente.", "success")
            return redirect(url_for('Docente.asistencia', curso_id=curso_id))

        except Exception as e:
            db.session.rollback()
            print("Error al registrar asistencia:", e)
            flash("Ocurrió un error al registrar la asistencia.", "danger")
            return redirect(url_for('Docente.asistencia', curso_id=curso_id))

    return render_template(
        'Docentes/Asistencia.html',
        cursos=cursos,
        curso_seleccionado=curso_seleccionado,
        estudiantes=estudiantes,
        estados_previos=estados_previos,
    )

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


@Docente_bp.route('/excusas_inasistencias')
@login_required
def excusas_inasistencias():
    """Lista de excusas de inasistencia enviadas por acudientes."""

    q = request.args.get('q', type=str, default='').strip()
    estado = request.args.get('estado', type=str, default='').strip() or None

    # Alias para estudiante y usuario acudiente
    Estudiante = aliased(Usuario)
    AcudienteUser = aliased(Usuario)

    # Base: detalles con excusa
    query = (
        db.session.query(
            Detalle_Asistencia,
            Asistencia,
            Estudiante,
            Acudiente,
            AcudienteUser,
        )
        .join(Asistencia, Detalle_Asistencia.ID_Asistencia == Asistencia.ID_Asistencia)
        .join(Estudiante, Detalle_Asistencia.ID_Estudiante == Estudiante.ID_Usuario)
        .join(Acudiente, Detalle_Asistencia.ID_Acudiente == Acudiente.ID_Acudiente)
        .join(AcudienteUser, Acudiente.ID_Usuario == AcudienteUser.ID_Usuario)
        .filter(Detalle_Asistencia.TextoExcusa.isnot(None))
    )

    # Filtro por nombre de acudiente
    if q:
        like = f"%{q}%"
        query = query.filter(
            (AcudienteUser.Nombre.ilike(like)) |
            (AcudienteUser.Apellido.ilike(like))
        )

    # Filtro por estado de excusa
    if estado:
        query = query.filter(Detalle_Asistencia.EstadoExcusa == estado)

    resultados = query.order_by(Asistencia.Fecha.desc(), Detalle_Asistencia.ID_Detalle_Asistencia.desc()).all()

    excusas = []
    for det, asis, est, rel, u_acu in resultados:
        excusas.append({
            'fecha_falta': asis.Fecha.strftime('%d/%m/%Y') if asis and asis.Fecha else '—',
            'estudiante_nombre': f"{est.Apellido} {est.Nombre}",
            'acudiente_nombre': f"{u_acu.Apellido} {u_acu.Nombre}",
            'texto_excusa': det.TextoExcusa,
            'archivo_excusa': det.ArchivoExcusa,
            'estado_excusa': det.EstadoExcusa,
        })

    return render_template('Docentes/ExcusasInasistencias.html', excusas=excusas, q=q, estado=estado)

@Docente_bp.route('/notas_curso/<int:curso_id>')
def notas_curso(curso_id):
    return render_template("Docentes/notas_curso.html", curso_id=curso_id)


# En routes/Docente.py


def _calcular_promedio_local(registro_nota):
    """Calcula el promedio de las notas que no son None (vacías)."""
    notas = [
        registro_nota.Nota_1, registro_nota.Nota_2, registro_nota.Nota_3, 
        registro_nota.Nota_4, registro_nota.Nota_5
    ]
    
    # Convierte None a 0 temporalmente para facilitar la suma, o mejor, filtra solo los que tienen valor.
    # Usaremos el filtro para no incluir notas no registradas en el cálculo.
    notas_validas = [n for n in notas if n is not None and n >= 0]
    
    if notas_validas:
        # Calcula el promedio y lo redondea a 2 decimales
        promedio = sum(notas_validas) / len(notas_validas)
        return round(promedio, 2)
    return None


# routes/Docente.py

# 🛑 NOTA: Cambiamos el nombre de la función y del parámetro a 'curso_id'
# routes/Docente.py

# administres.py (Función registro_notas_curso MEJORADA)

@Docente_bp.route('/registro_notas_curso/<int:curso_id>', methods=['GET', 'POST'])
@login_required
def registro_notas_curso(curso_id):
    """Pantalla de registro de notas.

    Admite dos tipos de identificador en la URL:
    - ID_Curso real (clave primaria de la tabla Curso)
    - Código "visible" como 601, 701, 1001, 1103, etc. (grado*100 + grupo)

    Si recibe un código (>=100), se decodifica a grado y grupo y se
    busca el Curso correspondiente. A partir de ahí se trabaja siempre
    con el ID_Curso real para consultas y formularios.
    """

    ID_DOCENTE_ACTUAL = current_user.ID_Usuario

    # --- 1. Resolver el curso real (ID_Curso) a partir del parámetro ---
    curso_obj = Curso.query.get(curso_id)
    curso_pk = None

    if not curso_obj and curso_id >= 100:
        # Interpretar como código grado*100 + grupo
        grado_calc = curso_id // 100
        grupo_calc = curso_id % 100

        # Aceptar grupo "1" y "01", "2" y "02", etc.
        grupo_candidatos = {str(grupo_calc), f"{grupo_calc:02d}"}

        curso_obj = Curso.query.filter(
            (Curso.Grado == str(grado_calc)) | (Curso.Grado == grado_calc),
            (Curso.Grupo.in_(list(grupo_candidatos)))
        ).first()

    if curso_obj:
        curso_pk = curso_obj.ID_Curso
    else:
        # Fallback: usamos el ID tal cual para que al menos no rompa,
        # pero el nombre mostrará "Curso Desconocido".
        curso_pk = curso_id

    # Mostrar preferiblemente el código visible del curso (por ejemplo 601)
    if curso_obj and hasattr(curso_obj, 'Grupo'):
        # Si el grupo ya contiene el código completo (601, 701, etc.), úsalo tal cual
        curso_nombre = f"{curso_obj.Grupo}"
    elif curso_obj and hasattr(curso_obj, 'Grado'):
        curso_nombre = f"{curso_obj.Grado}-{getattr(curso_obj, 'Grupo', '')}"
    else:
        curso_nombre = "Curso Desconocido"

    # 1.2. Claves de sesión para este curso específico (usando el ID real)
    session_key_asignatura = f'last_asignatura_{curso_pk}'
    session_key_periodo = f'last_periodo_{curso_pk}'
    
    # 1.3. Obtener filtros, priorizando: 1. URL/GET, 2. Sesión
    
    # Intentar obtener de la URL/GET
    asignatura_id_str = request.args.get('asignatura')
    periodo_str = request.args.get('periodo')

    # Si no están en la URL, intentar obtener de la Sesión para persistencia
    if not asignatura_id_str and session_key_asignatura in session:
        asignatura_id_str = str(session[session_key_asignatura])
        
    if not periodo_str and session_key_periodo in session:
        periodo_str = str(session[session_key_periodo])
        
    # Convertir a entero (usar 0 si no hay valor en la URL ni en la sesión)
    try:
        asignatura_id = int(asignatura_id_str or 0)
        periodo_seleccionado = int(periodo_str or 0)
    except ValueError:
        asignatura_id = 0
        periodo_seleccionado = 0
        
    # 1.4. Si se obtuvieron valores válidos, guardarlos en la sesión (para que persistan)
    if asignatura_id > 0 and periodo_seleccionado > 0:
        session[session_key_asignatura] = asignatura_id
        session[session_key_periodo] = periodo_seleccionado

    # 1.5. Obtener la lista de estudiantes matriculados (Ordenados por apellido y nombre)
    estudiantes_db = db.session.query(Usuario, Matricula). \
        join(Matricula, Matricula.ID_Estudiante == Usuario.ID_Usuario). \
        filter(
            Matricula.ID_Curso == curso_pk,
            Usuario.Rol == 'Estudiante'
        ).order_by(Usuario.Apellido, Usuario.Nombre).all()

    # 1.6. Obtener las asignaturas disponibles
    # Por ahora cargamos todas las asignaturas registradas, sin filtrar por docente,
    # para que siempre aparezcan en el combo aunque aún no exista Docente_Asignatura.
    asignaturas_db = (
        db.session.query(
            Asignatura.ID_Asignatura.label('id'),
            Asignatura.Nombre.label('nombre')
        )
        .order_by(Asignatura.Nombre)
        .all()
    )

    # 1.6.1. Agrupar por nombre base (primera palabra) para no repetir materias por grado
    asignaturas_unicas_dict = {}
    for asig in asignaturas_db:
        partes = (asig.nombre or '').split()
        nombre_base = partes[0] if partes else asig.nombre
        if nombre_base not in asignaturas_unicas_dict:
            asignaturas_unicas_dict[nombre_base] = asig

    asignaturas_unicas = list(asignaturas_unicas_dict.values())
    
    # --- 2. OBTENER NOTAS EXISTENTES (PERSISTENCIA) ---
    notas_por_estudiante = {}
    lista_estudiantes = []

    if asignatura_id > 0 and periodo_seleccionado > 0:
        # Consulta de notas solo si hay filtros válidos
        notas_db = Nota_Calificaciones.query.filter_by(
            ID_Asignatura=asignatura_id,
            Periodo=periodo_seleccionado
        ).all()
        try:
            print(f"[registro_notas_curso] Registros cargados para asig={asignatura_id}, periodo={periodo_seleccionado}: {len(notas_db)}")
        except Exception:
            pass
        
        # Mapear las notas por ID de Estudiante para acceso rápido en la plantilla
        notas_por_estudiante = {nota.ID_Estudiante: nota for nota in notas_db}

    # 3. Preparar la lista de estudiantes con sus notas
    for usuario, matricula in estudiantes_db:
        estudiante_id = usuario.ID_Usuario
        
        # Obtener el registro de nota o usar None si no existe
        registro_nota = notas_por_estudiante.get(estudiante_id)

        lista_estudiantes.append({
            'ID_Usuario': estudiante_id,
            'Nombre': usuario.Nombre,
            'Apellido': usuario.Apellido,
            'Promedio_Final': registro_nota.Promedio_Final if registro_nota else None,
            'registro_nota': registro_nota # Pasar el objeto completo para acceder a Nota_1, Nota_2, etc.
        })
        
    # 4. Renderizar la plantilla
    return render_template('Docentes/RegistroNotas.html',
                           curso_obj=curso_obj,
                           curso_nombre=curso_nombre, 
                           estudiantes=lista_estudiantes, 
                           curso_id=curso_pk, 
                           asignatura_id=asignatura_id,
                           periodo_seleccionado=periodo_seleccionado, # Pasar el filtro seleccionado
                           asignaturas=asignaturas_unicas
                           )
    
@Docente_bp.route('/generar_reporte_pdf/<int:curso_id>', methods=['GET'])
def generar_reporte_pdf(curso_id):
    
    # 0. Obtener filtros de la URL (vienen del redirect POST/GET)
    asignatura_id_str = request.args.get('asignatura', '0')
    periodo_str = request.args.get('periodo', '0')
    
    # 0.1. Validar y convertir a entero
    try:
        asignatura_id = int(asignatura_id_str)
        periodo = int(periodo_str)
    except ValueError:
        flash("Error: Los filtros de Asignatura o Período no son válidos.", "error")
        return redirect(url_for('Docente.registro_notas_curso', curso_id=curso_id))

    # --- 1. OBTENER DATOS DE LA BASE DE DATOS ---
    
    curso_obj = Curso.query.get_or_404(curso_id)
    asignatura_obj = Asignatura.query.get_or_404(asignatura_id)
    
    # 1.1. Obtener todos los estudiantes matriculados en el curso
    # Se une Matricula con Usuario para obtener los nombres
    estudiantes_query = db.session.query(Usuario).join(Matricula, Usuario.ID_Usuario == Matricula.ID_Estudiante).filter(
        Matricula.ID_Curso == curso_id
    ).order_by(Usuario.Apellido, Usuario.Nombre).all()

    estudiantes_con_notas = []
    
    # 1.2. Iterar sobre estudiantes para adjuntar sus notas
    for estudiante in estudiantes_query:
        # Buscar la nota para el período y asignatura específicos
        registro_nota = Nota_Calificaciones.query.filter_by(
            ID_Estudiante=estudiante.ID_Usuario,
            ID_Asignatura=asignatura_id,
            Periodo=periodo
        ).first()

        # Crear un diccionario de datos para la plantilla
        datos_estudiante = {
            'ID_Usuario': estudiante.ID_Usuario,
            'NombreCompleto': f"{estudiante.Apellido} {estudiante.Nombre}",
            # Proporcionar el objeto Nota_Calificaciones o un objeto vacío para evitar errores
            'registro_nota': registro_nota if registro_nota else Nota_Calificaciones(),
            'Promedio_Final': registro_nota.Promedio_Final if registro_nota else None
        }
        estudiantes_con_notas.append(datos_estudiante)

    # --- 2. Renderizar la plantilla del PDF ---
    # Debes crear el archivo 'templates/Docentes/ReporteNotas.html'
    html_out = render_template(
        'Docentes/ReporteNotas.html',
        curso_nombre=f"{curso_obj.Grado} {curso_obj.Grupo}",
        asignatura_nombre=asignatura_obj.Nombre,
        periodo=periodo,
        estudiantes=estudiantes_con_notas # Pasamos la lista de estudiantes con sus notas
    )
    
    # --- 3. Generar el PDF usando xhtml2pdf ---
    result_file = io.BytesIO()

    # Usamos io.BytesIO() para capturar la salida binaria del PDF
    pisa_status = pisa.CreatePDF(
        io.StringIO(html_out),  # El HTML renderizado como fuente
        dest=result_file,       # El objeto BytesIO como destino
        encoding='utf-8'
    )
    
    # Verifica si la generación fue exitosa
    if pisa_status.err:
        flash("Error al generar el PDF del reporte de notas.", "error")
        return redirect(url_for('Docente.registro_notas_curso', curso_id=curso_id))
    
    # --- 4. Devolver la respuesta al navegador ---
    result_file.seek(0)
    pdf = result_file.read()
    
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    
    # Nombre de archivo dinámico
    filename = f'Reporte_Notas_{asignatura_obj.Nombre}_{curso_obj.Grado}{curso_obj.Grupo}_P{periodo}.pdf'
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'
    
    return response

# ✅ ESTA ES LA DEFINICIÓN CORRECTA PARA PETICIONES AJAX POST ✅
@Docente_bp.route('/cargar_notas_ajax', methods=['POST'])
def cargar_notas_ajax():
    # Los datos se obtienen del cuerpo JSON, no de la URL
    data = request.get_json()
    curso_id = data.get('curso_id')
    asignatura_id = data.get('asignatura_id')
    periodo = data.get('periodo')
    
    # ... (El resto de tu lógica de Python) ...




# --- RUTA PRINCIPAL DE GUARDADO ---
# routes/Docente.py

@Docente_bp.route('/guardar_notas_curso/<int:curso_id>', methods=['POST'])
def guardar_notas_curso(curso_id):
    
    # Define las claves de sesión basadas en el ID del curso
    session_key_asignatura = f'last_asignatura_{curso_id}'
    session_key_periodo = f'last_periodo_{curso_id}'
    
    datos_formulario = request.form
    
    # 1. Obtener acción y filtros
    accion = datos_formulario.get('action', 'guardar') 
    asignatura_id_str = datos_formulario.get('asignatura')
    periodo_str = datos_formulario.get('periodo')
    
    # 1.1. Validar filtros
    if not asignatura_id_str or not periodo_str:
        flash("Error: Seleccione la Asignatura y el Período antes de guardar o reportar.", "error")
        return redirect(url_for('Docente.registro_notas_curso', curso_id=curso_id))
    
    try:
        asignatura_id = int(asignatura_id_str)
        periodo = int(periodo_str)
    except ValueError:
        flash("Error: Los filtros de Asignatura o Período no son válidos.", "error")
        return redirect(url_for('Docente.registro_notas_curso', curso_id=curso_id))

    # 2. PROCESAMIENTO DE NOTAS 
    try:
        # DEBUG: contar campos de notas y mostrar muestra
        nota_items = [(k, v) for k, v in datos_formulario.items() if k.startswith('nota_')]
        print(f"[guardar_notas_curso] Campos de notas recibidos: {len(nota_items)}")
        print(f"[guardar_notas_curso] Muestra notas: {nota_items[:5]}")

        # Agrupar notas por estudiante para calcular promedio
        por_estudiante = {}
        for key, value in nota_items:
            partes = key.split('_')  # ['nota', 'n', 'id']
            if len(partes) != 3:
                continue
            n = partes[1]
            est_id = int(partes[2])
            if est_id not in por_estudiante:
                por_estudiante[est_id] = {}
            if value and value.strip() != '':
                try:
                    por_estudiante[est_id][f'Nota_{n}'] = float(value)
                except ValueError:
                    pass

        updated_estudiante_ids = set()
        for est_id, notas_dict in por_estudiante.items():
            # Buscar o crear el registro de Nota_Calificaciones para este estudiante/asignatura/período
            nota_obj = Nota_Calificaciones.query.filter_by(
                ID_Estudiante=est_id,
                ID_Asignatura=asignatura_id,
                Periodo=periodo
            ).first()

            if not nota_obj:
                # Asegurar que exista un Historial_Academico asociado a la matrícula del estudiante
                curso_obj = Curso.query.get(curso_id)
                matricula = Matricula.query.filter_by(ID_Estudiante=est_id, ID_Curso=curso_id).first()

                historial = None
                if matricula and curso_obj:
                    historial = Historial_Academico.query.filter_by(
                        ID_Matricula=matricula.ID_Matricula,
                        Anio=curso_obj.Anio,
                        Periodo=str(periodo)
                    ).first()

                    if not historial:
                        historial = Historial_Academico(
                            ID_Matricula=matricula.ID_Matricula,
                            Anio=curso_obj.Anio,
                            Periodo=str(periodo),
                            Descripcion=f"Notas período {periodo}",
                            Observaciones=""
                        )
                        db.session.add(historial)
                        # No hacemos commit aún; se hará al final del bloque

                # Si por alguna razón no hay historial, no podemos crear la nota (rompería la FK)
                if not historial:
                    continue

                # Crear la nota y enlazarla al historial usando la relación ORM
                nota_obj = Nota_Calificaciones(
                    ID_Estudiante=est_id,
                    ID_Asignatura=asignatura_id,
                    Periodo=periodo
                )
                nota_obj.historial = historial
                db.session.add(nota_obj)

            # Asignar campos Nota_1..Nota_5 según lo recibido
            for campo, val in notas_dict.items():
                if hasattr(nota_obj, campo):
                    setattr(nota_obj, campo, val)

            # Calcular y guardar promedio
            if notas_dict:
                prom = round(sum(notas_dict.values()) / len(notas_dict), 2)
                nota_obj.Promedio_Final = prom

            updated_estudiante_ids.add(est_id)

        db.session.commit()

        # DEBUG: verificar cuántos registros hay ahora
        try:
            cnt = Nota_Calificaciones.query.filter_by(ID_Asignatura=asignatura_id, Periodo=periodo).count()
            print(f"[guardar_notas_curso] Registros ahora para asig={asignatura_id}, periodo={periodo}: {cnt}")
        except Exception as _:
            pass
        
        # 2.1. Notificaciones automáticas a estudiantes y acudientes
        try:
            notis = []
            asig = Asignatura.query.get(asignatura_id)
            asignatura_nombre = asig.Nombre if asig else f"Asignatura {asignatura_id}"
            for est_id in updated_estudiante_ids:
                est = Usuario.query.get(est_id)
                nombre_est = f"{est.Nombre} {est.Apellido}" if est else f"Estudiante {est_id}"
                # Notificación al estudiante
                notis.append(Notificacion(
                    Titulo='Nueva calificación registrada',
                    Mensaje=f"Se registró/actualizó una calificación en {asignatura_nombre}, período {periodo}.",
                    Enlace=None,
                    ID_Usuario=est_id
                ))
                # Notificaciones a acudientes relacionados y activos
                relaciones = Acudiente.query.filter_by(ID_Estudiante=est_id, Estado='Activo').all()
                print(f"[guardar_notas_curso] Estudiante {est_id}: acudientes activos encontrados = {len(relaciones)}")
                if relaciones:
                    print(f"[guardar_notas_curso] Acudientes IDs: {[r.ID_Usuario for r in relaciones]}")
                for rel in relaciones:
                    notis.append(Notificacion(
                        Titulo='Nueva calificación del estudiante',
                        Mensaje=f"El estudiante {nombre_est} tiene una nueva calificación en {asignatura_nombre}, período {periodo}.",
                        Enlace=None,
                        ID_Usuario=rel.ID_Usuario
                    ))
            if notis:
                db.session.bulk_save_objects(notis)
                db.session.commit()
                print(f"[guardar_notas_curso] Notificaciones creadas: {len(notis)}")
        except Exception as e:
            db.session.rollback()
            try:
                print(f"[guardar_notas_curso] Error creando notificaciones: {e}")
            except Exception:
                pass

        # ✅ CLAVE DE PERSISTENCIA: Guardar los filtros en la sesión
        session[session_key_asignatura] = asignatura_id
        session[session_key_periodo] = periodo

        flash("Notas guardadas exitosamente.", "success")
        
    except Exception as e:
        db.session.rollback()
        flash(f"Error al guardar los cambios en la base de datos: {e}", "error")

    # 3. REDIRECCIONAMIENTO FINAL (según la acción solicitada)
    if accion == 'reporte':
        # Redirigir a la generación de PDF (usa GET)
        return redirect(url_for(
            'Docente.generar_reporte_pdf', 
            curso_id=curso_id, 
            asignatura=asignatura_id, 
            periodo=periodo
        ))

    # Si la acción es 'guardar' o cualquier otra, redirigir de nuevo a la vista
    # manteniendo los filtros en la URL para recargar la tabla actualizada.
    return redirect(url_for(
        'Docente.registro_notas_curso', 
        curso_id=curso_id,
        asignatura=asignatura_id, 
        periodo=periodo
    ))



@Docente_bp.route('/notas_registro')
def notas_registro():
    return render_template('Docentes/Notas_Registro.html')

@Docente_bp.route('/notas_consultar')
def notas_consultar():
    return render_template('Docentes/Notas_Consultar.html')

@Docente_bp.route('/calculo_promedio')
def calculo_promedio():
    return render_template('Docentes/CalculoPromedio.html')



# GESTIÓN DE LA OBSERVACIÓN

@Docente_bp.route('/observador')
def observador():
    # Traer observaciones con sus estudiantes y cursos
    observaciones = (
        db.session.query(Observacion, Usuario, Curso)
        .join(Matricula, Observacion.ID_Matricula == Matricula.ID_Matricula)
        .join(Usuario, Matricula.ID_Estudiante == Usuario.ID_Usuario)
        .join(Curso, Matricula.ID_Curso == Curso.ID_Curso)
        .all()
    )

    # Traer todos los estudiantes
    estudiantes = Usuario.query.filter_by(Rol='Estudiante').all()

    # Traer todos los cursos
    cursos = Curso.query.all()

    # Traer todas las matrículas (por si se usan más adelante)
    matriculas = Matricula.query.all()

    return render_template(
        'docentes/observador.html',
        observaciones=observaciones,
        estudiantes=estudiantes,
        cursos=cursos,
        matriculas=matriculas
    )


@Docente_bp.route('/agregar_observacion', methods=['POST'])
def agregar_observacion():
    try:
        id_estudiante = request.form['id_estudiante']
        id_curso = request.form['id_curso']
        descripcion = request.form['descripcion']
        tipo = request.form['tipo']
        nivel_importancia = request.form['nivelImportancia']
        recomendacion = request.form['recomendacion']

        # Buscar la matrícula correspondiente al estudiante y curso
        matricula = Matricula.query.filter_by(ID_Estudiante=id_estudiante, ID_Curso=id_curso).first()
        if not matricula:
            flash('❌ No se encontró la matrícula para el estudiante en ese curso.', 'danger')
            return redirect(url_for('Docente.observador'))

        nueva_observacion = Observacion(
            Fecha=date.today(),
            Descripcion=descripcion,
            Tipo=tipo,
            NivelImportancia=nivel_importancia,
            Recomendacion=recomendacion,
            Estado='Activa',
            ID_Horario=None,
            ID_Matricula=matricula.ID_Matricula
        )

        db.session.add(nueva_observacion)
        db.session.commit()
        flash('✅ Observación agregada correctamente', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error al agregar observación: {e}', 'danger')

    return redirect(url_for('Docente.observador'))



@Docente_bp.route('/horarios')
def horarios():
    return render_template('Docentes/Horarios.html')




# ----------------- SUB-PÁGINAS -----------------

#--------------------------material de apoyo----------------------------
@Docente_bp.route('/materialapoyo')
@login_required
def materialapoyo():
    cursos = db.session.query(Curso)\
                .join(Docente_Asignatura, Docente_Asignatura.ID_Curso == Curso.ID_Curso)\
                .filter(Docente_Asignatura.ID_Docente == current_user.ID_Usuario)\
                .all()

    return render_template('Docentes/MaterialApoyo.html', cursos=cursos)

@Docente_bp.route('/materialapoyo/<int:curso_id>', methods=['GET', 'POST'])
@login_required
def materialapoyo2(curso_id):

    # Cargar las materias dictadas por este docente en este curso
    materias = (
        db.session.query(Asignatura)
        .join(Docente_Asignatura)
        .filter(
            Docente_Asignatura.ID_Docente == current_user.ID_Usuario,
            Docente_Asignatura.ID_Curso == curso_id
        )
        .all()
    )

    if request.method == 'POST':

        tipo = request.form.get('tipo')
        asignatura_nombre = request.form.get('nombre')
        archivo = request.files.get('archivo')
        link = request.form.get('link')

        # --- Buscar materia ---
        asignatura = Asignatura.query.filter_by(Nombre=asignatura_nombre).first()

        if not asignatura:
            flash("La materia seleccionada no es válida.", "danger")
            return redirect(url_for('Docente.materialapoyo2', curso_id=curso_id))

        ruta_archivo = None
        enlace_final = None

        # === 1. Crear carpeta material si no existe ===
        carpeta_material = os.path.join(current_app.static_folder, "material")
        os.makedirs(carpeta_material, exist_ok=True)

        # === 2. Guardar archivo según tipo ===
        if archivo and archivo.filename != "" and tipo not in ["Enlace", "Video"]:
            filename = secure_filename(archivo.filename)
            ruta_archivo = f"material/{filename}"
            archivo.save(os.path.join(current_app.static_folder, ruta_archivo))

        # === 3. Guardar enlace si aplica ===
        if tipo in ["Enlace", "Video"]:
            enlace_final = link

        # === 4. Guardar registro en la BD ===
        material = MaterialDidactico(
            ID_Docente=current_user.ID_Usuario,
            ID_Curso=curso_id,
            Titulo=asignatura_nombre,
            Tipo=tipo,
            RutaArchivo=ruta_archivo,
            Enlace=enlace_final
        )

        db.session.add(material)
        db.session.commit()

        flash('Material subido correctamente.', 'success')
        return redirect(url_for('Docente.materialapoyo2', curso_id=curso_id))

    # Cargar material existente
    materiales = MaterialDidactico.query.filter_by(
        ID_Docente=current_user.ID_Usuario,
        ID_Curso=curso_id
    ).all()

    return render_template(
        'Docentes/MaterialApoyo2.html',
        materiales=materiales,
        curso_id=curso_id,
        materias=materias
    )



#----------------------------------------------------

@Docente_bp.route('/registrotutorias2')
def registrotutorias2():
    return render_template('Docentes/RegistroTutorías2.html')

@Docente_bp.route('/inasistencias')
def inasistencias():
    return render_template('Docentes/inasistencias.html')


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
"""@Docente_bp.route('/api/crear_actividad/<int:curso_id>', methods=['POST'], endpoint='api_crear_actividad')
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

    return render_template('Docente/Crear_Actividad.html', curso_id=curso_id)"""


#@Docente_bp.route('/crear_actividad/<int:curso_id>', methods=['GET', 'POST'], endpoint='form_crear_actividad')
#@login_required
#def form_crear_actividad(curso_id):
#    return render_template('Docentes/Crear_Actividad.html', curso_id=curso_id)

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
                id_actividad = int(u.get('id_actividad'))
                matricula_id = int(u.get('matricula_id'))
                cal = u.get('calificacion')
                cal_val = None if cal in [None, ""] else float(cal)

                # --- Verificar existencia antes de insertar
                actividad = Actividad.query.get(id_actividad)
                matricula = Matricula.query.get(matricula_id)
                if not actividad or not matricula:
                    results['errors'].append({
                        'id_actividad': id_actividad,
                        'matricula_id': matricula_id,
                        'error': 'Actividad o matrícula no existe'
                    })
                    continue

                # --- Actualizar o crear registro
                row = Actividad_Estudiante.query.filter_by(
                    ID_Actividad=id_actividad, ID_Matricula=matricula_id
                ).first()
                if row:
                    row.Calificacion = cal_val
                    results['saved'] += 1
                else:
                    nueva = Actividad_Estudiante(
                        ID_Actividad=id_actividad,
                        ID_Matricula=matricula_id,
                        Observaciones='',
                        Calificacion=cal_val
                    )
                    db.session.add(nueva)
                    results['created'] += 1

            except Exception as row_error:
                results['errors'].append({
                    'id_actividad': u.get('id_actividad'),
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


