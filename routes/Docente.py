from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session, current_app
from flask_login import login_required, current_user
from flask_mail import Message
from werkzeug.utils import secure_filename


from Controladores.models import ( db, Usuario, Matricula, Asignatura, Cronograma_Actividades, Actividad, Actividad_Estudiante, Periodo, Curso, Notificacion, Programacion, Observacion, Nota_Calificaciones, Docente_Asignatura, ResumenSemanal, Tutorias )

from datetime import date
import os

import datetime


from decimal import Decimal


#Definir el Blueprint para el administardor
Docente_bp = Blueprint('Docente', __name__, url_prefix='/docente')
ID_DOCENTE_FIJO = 2




@Docente_bp.route('/paginainicio')
def paginainicio():
    return render_template('Docentes/Paginainicio_Docentes.html')

# ---------------- NOTIFICACIONES DOCENTE----------------


@Docente_bp.route('/notificaciones', methods=['GET'])
def obtener_notificaciones():
    user_id = session.get('user_id')
    notificaciones = Notificacion.query.filter_by(ID_Usuario=user_id, Estado='No leída').all()
    return jsonify([
        {"asunto": n.Asunto, "mensaje": n.Mensaje, "fecha": n.Fecha.strftime("%d-%m-%Y %H:%M")}
        for n in notificaciones
    ])
    
@Docente_bp.route("/notificaciones/recibir")
@login_required
def recibir_notificaciones():
    usuario = current_user  # depende de tu setup con Flask-Login
    notis = Notificacion.query.filter_by(usuario_id=usuario.id, leida=False).all()
    lista = [{"titulo": n.titulo, "mensaje": n.mensaje} for n in notis]
    return jsonify(lista)

@Docente_bp.route('/manual')
def manual():
    return render_template('Docentes/ManualUsuario.html')

@Docente_bp.route('/materialapoyo')
def materialapoyo():
    return render_template('Docentes/MaterialApoyo.html')

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


# En routes/Docente.py


def calcular_promedio(registro_notas):
    """Calcula el promedio de las 5 notas, ignorando valores None."""
    notas_validas = []
    
    for i in range(1, 6):
        columna = f'Nota_{i}'
        valor = getattr(registro_notas, columna, None)
        if valor is not None:
            notas_validas.append(float(valor))

    if not notas_validas:
        return None
    
    promedio = sum(notas_validas) / len(notas_validas)
    return round(promedio, 1)


# routes/Docente.py

# 🛑 NOTA: Cambiamos el nombre de la función y del parámetro a 'curso_id'
# routes/Docente.py

@Docente_bp.route('/registro_notas_curso/<int:curso_id>', methods=['GET', 'POST'])
def registro_notas_curso(curso_id):
    
    # 1. Obtener la información del curso
    curso_obj = Curso.query.get(curso_id)
    
    # 🛑 CORRECCIÓN: Usar el atributo correcto (reemplaza 'NombreCurso' si el tuyo es diferente)
    # Si la depuración te dijo que el atributo es 'Nombre_Completo_Curso', úsalo aquí.
    if curso_obj:
        print("--- DEBUG CURSO OBJETO ---")
        print(f"Tipo de objeto: {type(curso_obj)}")
        print(f"Atributos disponibles: {dir(curso_obj)}")
        print("----------------------------")
    curso_nombre = curso_obj.NOMBRE_CURSO if curso_obj and hasattr(curso_obj, 'NOMBRE_CURSO') else "Curso Desconocido"
    
        
    
    # 2. Obtener la lista de estudiantes matriculados en ESE CURSO
    estudiantes_db = db.session.query(Usuario, Matricula). \
        join(Matricula, Matricula.ID_Estudiante == Usuario.ID_Usuario). \
        filter(
            Matricula.ID_Curso == curso_id,
            Usuario.Rol == 'Estudiante'
        ).all()

    # 3. Preparar la lista de estudiantes (Sin cambios)
    lista_estudiantes = []
    for usuario, matricula in estudiantes_db:
        # Aquí también hay una potencial mejora: si tu modelo Usuario tiene los campos como
        # .nombre y .apellido (minúscula), deberías cambiarlos aquí, pero lo dejaré 
        # con .Nombre y .Apellido asumiendo que funciona.
        lista_estudiantes.append({
            'ID_Usuario': usuario.ID_Usuario,
            'Nombre': usuario.Nombre,
            'Apellido': usuario.Apellido,
            'Promedio_Final': None,
            'nota_1': None,
            'notas_existentes': {}
        })

    # 4. Obtener las asignaturas (Sin cambios)
    ID_DOCENTE_ACTUAL = 2 # 🛑 Reemplazar con session.get('ID_Usuario') o similar
    asignaturas_db = db.session.query(Asignatura.ID_Asignatura.label('id'), 
                                       Asignatura.Nombre.label('nombre'))\
                               .join(Docente_Asignatura, Docente_Asignatura.ID_Asignatura == Asignatura.ID_Asignatura)\
                               .filter(Docente_Asignatura.ID_Docente == ID_DOCENTE_ACTUAL)\
                               .distinct()\
                               .all()

    return render_template('Docentes/RegistroNotas.html',
                           curso_obj=curso_obj,
                           curso_nombre=curso_nombre, # Ahora contiene el nombre real (si el atributo es correcto)
                           estudiantes=lista_estudiantes, 
                           curso_id=curso_id, 
                           asignatura_id=0,
                           asignaturas=asignaturas_db
                           )

# ----------------------------------------------------------------------
# RUTA DE GUARDADO AJAX (Sin cambios, se mantiene para completar el contexto)
# ----------------------------------------------------------------------

# routes/Docente.py
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
@Docente_bp.route('/guardar_notas_curso/<int:curso_id>', methods=['POST'])
def guardar_notas_curso(curso_id):
    
    # --- FUNCIÓN DE CÁLCULO DE PROMEDIO (LOCAL RENOMBRADA) ---
    # Usamos un nombre único (_calcular_promedio_local) para que Flask no la registre como endpoint.
    def _calcular_promedio_local(registro_nota, ):
        """Calcula el promedio de las notas que no son None (vacías)."""
        notas = [
            registro_nota.Nota_1, registro_nota.Nota_2, registro_nota.Nota_3, 
            registro_nota.Nota_4, registro_nota.Nota_5
        ]
        
        notas_validas = [n for n in notas if n is not None]
        
        if notas_validas:
            # Calcula el promedio y lo redondea a 2 decimales
            promedio = sum(notas_validas) / len(notas_validas)
            return round(promedio, 2)
        return None
    # ------------------------------------------------
    
    datos_formulario = request.form
    
    # 1. Obtener filtros de asignatura y período
    asignatura_id = datos_formulario.get('asignatura')
    periodo = datos_formulario.get('periodo')
    
    if not asignatura_id or not periodo:
        flash("Error: Seleccione la Asignatura y el Período antes de guardar.", "error")
        return redirect(url_for('Docente.registro_notas_curso', curso_id=curso_id))
    
    # 2. Iterar sobre los datos del formulario y preparar/actualizar registros
    for key, value in datos_formulario.items():
        if key.startswith('nota_'):
            
            try:
                # Extrae Estudiante ID y número de nota (1 a 5)
                partes = key.split('_')
                numero_nota = partes[1] 
                id_usuario = int(partes[2]) 
                
                # Convierte a float. Si está vacío, se usa None.
                valor_nota = float(value) if value and value.strip() != '' else None 
                
                # 3. Buscar el registro de la nota
                registro_nota = Nota_Calificaciones.query.filter_by(
                    ID_Estudiante=id_usuario,
                    ID_Asignatura=asignatura_id,
                    Periodo=periodo
                ).first()
                
                # 4. CREACIÓN / ACTUALIZACIÓN
                if not registro_nota:
                    # Crea un nuevo registro si no existe
                    registro_nota = Nota_Calificaciones(
                        ID_Estudiante=id_usuario,
                        ID_Asignatura=asignatura_id,
                        Periodo=periodo
                    )
                    db.session.add(registro_nota)
                
                # 5. Aplicar la nota al campo correcto (Ej: Nota_1, Nota_2, etc.)
                nombre_campo_db = f'Nota_{numero_nota}' 
                setattr(registro_nota, nombre_campo_db, valor_nota)

                # 6. Recalcular el promedio inmediatamente
                promedio = _calcular_promedio_local(registro_nota) 
                registro_nota.Promedio_Final = promedio

            except Exception as e:
                # Usa `continue` para pasar a la siguiente nota si hay un error
                print(f"🛑 ERROR CRÍTICO AL PROCESAR NOTA {key}: {e}")
                flash(f"Error al procesar la nota {key}: {e}", "warning")
                continue 

    # 7. Guardar todos los cambios en la base de datos
    try:
        db.session.commit()
        flash("Notas guardadas exitosamente.", "success")
        
    except Exception as e:
        db.session.rollback()
        flash(f"Error al guardar los cambios en la base de datos: {e}", "error")
        print(f"❌ DB ROLLBACK/ERROR FINAL: {e}")
        
    return redirect(url_for('Docente.registro_notas_curso', curso_id=curso_id))



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


