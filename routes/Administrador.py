from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import generate_password_hash
from sqlalchemy import func
from flask import jsonify
from datetime import datetime
from Controladores.models import db, Usuario, Matricula, Curso, Periodo, Asignatura, Docente_Asignatura, Programacion, Cronograma_Actividades, Actividad
from flask_mail import Message
from decimal import Decimal

#Definir el Blueprint para el administardor
Administrador_bp = Blueprint('Administrador', __name__, url_prefix='/administrador')


# ----------------- RUTAS DE INICIO -----------------
@Administrador_bp.route('/paginainicio')
def paginainicio():
    return render_template('Administrador/Paginainicio_Administrador.html')

# ----------------- DOCENTES -----------------
@Administrador_bp.route('/profesores')

def profesores():
    docentes = Usuario.query.filter_by(Rol='Docente').all()
    return render_template('Administrador/Profesores.html', docentes=docentes)

@Administrador_bp.route('/agregar_docente', methods=['POST'])
@login_required
def agregar_docente():
    try:
        nombre = request.form['Nombre']
        apellido = request.form['Apellido']
        correo = request.form['Correo']
        numero_doc = request.form['NumeroDocumento']
        telefono = request.form['Telefono']
        tipo_doc = "C.C."
        profesion = request.form['Profesion']
        ciclo = request.form['Ciclo']

        hashed_password = generate_password_hash("123456")

        nuevo_docente = Usuario(
            Nombre=nombre,
            Apellido=apellido,
            Correo=correo,
            Contrasena=hashed_password,
            TipoDocumento=tipo_doc,
            NumeroDocumento=numero_doc,
            Telefono=telefono,
            Rol='Docente',
            Estado='Activo',
            Direccion="",
            Genero="Otro"
        )
        db.session.add(nuevo_docente)
        db.session.commit()
        flash("Docente agregado correctamente", "success")
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f"Error al agregar docente: {str(e)}", "danger")

    return redirect(url_for('Administrador.profesores'))


@Administrador_bp.route('/actualizar_docente/<int:id>', methods=['POST'])
@login_required
def actualizar_docente(id):
    docente = Usuario.query.get_or_404(id)

    docente.Nombre = request.form['Nombre']
    docente.Apellido = request.form['Apellido']
    docente.TipoDocumento = request.form['TipoDocumento']
    docente.NumeroDocumento = request.form['NumeroDocumento']
    docente.Correo = request.form['Correo']
    docente.Telefono = request.form['Telefono']
    docente.Direccion = request.form['Profesion']
    docente.Calle = request.form['Ciclo']

    try:
        db.session.commit()
        flash("Docente actualizado correctamente.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error al actualizar: {e}", "danger")

    return redirect(url_for('Administrador.profesores'))


@Administrador_bp.route('/eliminar_docente/<int:id>', methods=['POST'])
@login_required
def eliminar_docente(id):
    docente = Usuario.query.get_or_404(id)
    try:
        db.session.delete(docente)
        db.session.commit()
        flash("Docente eliminado correctamente", "danger")
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f"Error al eliminar docente: {str(e)}", "danger")

    return redirect(url_for('Administrador.profesores'))


# ----------------- ESTUDIANTES -----------------
@Administrador_bp.route('/estudiantes')
@login_required
def estudiantes():
    estudiantes = Usuario.query.filter_by(Rol='Estudiante').all()
    return render_template('Administrador/Estudiantes.html', estudiantes=estudiantes)


@Administrador_bp.route('/agregar_estudiante', methods=['POST'])
@login_required
def agregar_estudiante():
    try:
        nombre = request.form['Nombre']
        apellido = request.form['Apellido']
        correo = request.form['Correo']
        numero_doc = request.form['NumeroDocumento']
        telefono = request.form['Telefono']
        tipo_doc = request.form['TipoDocumento']
        direccion = request.form['Direccion']
        curso = request.form['Curso']

        hashed_password = generate_password_hash("123456")

        nuevo_estudiante = Usuario(
            Nombre=nombre,
            Apellido=apellido,
            Correo=correo,
            Contrasena=hashed_password,
            TipoDocumento=tipo_doc,
            NumeroDocumento=numero_doc,
            Telefono=telefono,
            Rol='Estudiante',
            Estado='Activo',
            Direccion=direccion,
            Genero="Otro"
        )
        db.session.add(nuevo_estudiante)
        db.session.commit()
        flash("Estudiante agregado correctamente", "success")
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f"Error al agregar estudiante: {str(e)}", "danger")

    return redirect(url_for('Administrador.estudiantes'))


@Administrador_bp.route('/actualizar_estudiante/<int:id>', methods=['POST'])
@login_required
def actualizar_estudiante(id):
    estudiante = Usuario.query.get_or_404(id)

    estudiante.Nombre = request.form['Nombre']
    estudiante.Apellido = request.form['Apellido']
    estudiante.TipoDocumento = request.form['TipoDocumento']
    estudiante.NumeroDocumento = request.form['NumeroDocumento']
    estudiante.Correo = request.form['Correo']
    estudiante.Telefono = request.form['Telefono']
    estudiante.Direccion = request.form['Direccion']
    estudiante.Calle = request.form['Curso']

    try:
        db.session.commit()
        flash("Estudiante actualizado correctamente", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error al actualizar: {e}", "danger")

    return redirect(url_for('Administrador.estudiantes'))


@Administrador_bp.route('/eliminar_estudiante/<int:id>', methods=['POST'])
@login_required
def eliminar_estudiante(id):
    estudiante = Usuario.query.get_or_404(id)
    try:
        db.session.delete(estudiante)
        db.session.commit()
        flash("Estudiante eliminado correctamente", "danger")
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f"Error al eliminar estudiante: {str(e)}", "danger")

    return redirect(url_for('Administrador.estudiantes'))


# ----------------- ACUDIENTES -----------------
@Administrador_bp.route('/acudientes')
@login_required
def acudientes():
    acudientes = Usuario.query.filter_by(Rol='Acudiente').all()
    return render_template('Administrador/Acudientes.html', acudientes=acudientes)


@Administrador_bp.route('/agregar_acudiente', methods=['POST'])
@login_required
def agregar_acudiente():
    try:
        nombre = request.form['Nombre']
        apellido = request.form['Apellido']
        correo = request.form['Correo']
        numero_doc = request.form['NumeroDocumento']
        telefono = request.form['Telefono']
        tipo_doc = request.form['TipoDocumento']
        direccion = request.form['Direccion']

        hashed_password = generate_password_hash("123456")

        nuevo_acudiente = Usuario(
            Nombre=nombre,
            Apellido=apellido,
            Correo=correo,
            Contrasena=hashed_password,
            TipoDocumento=tipo_doc,
            NumeroDocumento=numero_doc,
            Telefono=telefono,
            Direccion=direccion,
            Rol='Acudiente',
            Estado='Activo',
            Genero="Otro"
        )
        db.session.add(nuevo_acudiente)
        db.session.commit()
        flash("Acudiente agregado correctamente", "success")
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f"Error al agregar acudiente: {str(e)}", "danger")

    return redirect(url_for('Administrador.acudientes'))


@Administrador_bp.route('/actualizar_acudiente/<int:id>', methods=['POST'])
@login_required
def actualizar_acudiente(id):
    acudiente = Usuario.query.get_or_404(id)

    acudiente.Nombre = request.form['Nombre']
    acudiente.Apellido = request.form['Apellido']
    acudiente.TipoDocumento = request.form['TipoDocumento']
    acudiente.NumeroDocumento = request.form['NumeroDocumento']
    acudiente.Correo = request.form['Correo']
    acudiente.Telefono = request.form['Telefono']
    acudiente.Direccion = request.form['Direccion']

    try:
        db.session.commit()
        flash("Acudiente actualizado correctamente.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error al actualizar: {e}", "danger")

    return redirect(url_for('Administrador.acudientes'))


@Administrador_bp.route('/eliminar_acudiente/<int:id>', methods=['POST'])
@login_required
def eliminar_acudiente(id):
    acudiente = Usuario.query.get_or_404(id)
    try:
        db.session.delete(acudiente)
        db.session.commit()
        flash("Acudiente eliminado correctamente", "danger")
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f"Error al eliminar acudiente: {str(e)}", "danger")

    return redirect(url_for('Administrador.acudientes'))


# ----------------- OTRAS VISTAS -----------------

@Administrador_bp.route ('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form.get('Nombre')
        apellido = request.form.get('Apellido')
        correo = request.form.get('Correo')
        contrasena = request.form.get('Contrasena')
        numero_documento = request.form.get('NumeroDocumento')
        telefono = request.form.get('Telefono')
        direccion = request.form.get('Direccion')
        rol = request.form.get('Rol')

        tipo_documento = request.form.get('TipoDocumento', 'CC')
        estado = request.form.get('Estado', 'Activo')
        genero = request.form.get('Genero', '')

        if not all([nombre, apellido, correo, contrasena, numero_documento, telefono, direccion, rol]):
            flash('Por favor, completa todos los campos requeridos.')
            return render_template('Administrador/Registro.html')

        try:
            existing_user = Usuario.query.filter_by(Correo=correo).first()
            if existing_user:
                flash('El correo ya está registrado.')
                return render_template('Administrador/Registro.html')

            hashed_password = generate_password_hash(contrasena)
            
            new_user = Usuario(
                Nombre=nombre,
                Apellido=apellido,
                Correo=correo,
                Contrasena=hashed_password,
                TipoDocumento=tipo_documento,
                NumeroDocumento=numero_documento,
                Telefono=telefono,
                Direccion=direccion,
                Rol=rol,
                Estado=estado,
                Genero=genero
            )
            
            
            db.session.add(new_user)
            db.session.commit()
        
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Error al registrar: {str(e)}')
            return render_template('Administrador/Registro.html')

    return render_template('Administrador/Registro.html')


@Administrador_bp.route('/api/repitentes', methods=['POST'])
@login_required
def api_agregar_repitente():
    try:
        data = request.get_json()

        # buscar estudiante por documento
        estudiante = Usuario.query.filter_by(NumeroDocumento=data.get('doc')).first()
        if not estudiante:
            return jsonify({"success": False, "error": "Estudiante no encontrado"}), 404

        # crear nueva matrícula (año actual, estado repitente)
        nueva_matricula = Matricula(
            ID_Estudiante=estudiante.ID_Usuario,
            AnioLectivo=datetime.now().year,
            Estado="Repitente"
        )
        db.session.add(nueva_matricula)
        db.session.commit()

        return jsonify({
            "success": True,
            "id": estudiante.ID_Usuario,
            "nombre": f"{estudiante.Nombre} {estudiante.Apellido}",
            "tipo": estudiante.TipoDocumento,
            "doc": estudiante.NumeroDocumento,
            "curso": data.get('curso'),
            "veces": Matricula.query.filter_by(ID_Estudiante=estudiante.ID_Usuario).count()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


@Administrador_bp.route('/manual')
def manual():
    return render_template('Administrador/ManualUsuario.html')


@Administrador_bp.route('/resumensemanal')
def resumensemanal():
    return render_template('Administrador/ResumenSemanal.html')


@Administrador_bp.route('/registrotutorias')
def registrotutorias():
    return render_template('Administrador/RegistroTutorías.html')


@Administrador_bp.route('/comunicacion')
def comunicacion():
    return render_template('Administrador/Comunicación.html')


@Administrador_bp.route('/reunion')
def reunion():
    return render_template('Administrador/Reunion.html')


@Administrador_bp.route('/noticias')
def noticias():
    return render_template('Administrador/Noticias.html')


@Administrador_bp.route('/circulares')
def circulares():
    return render_template('Administrador/Circulares.html')


@Administrador_bp.route('/noticias_vistas')
def noticias_vistas():
    return render_template('Administrador/NoticiasVistas.html')


@Administrador_bp.route('/usuarios')
def usuarios():
    return render_template('Administrador/Usuarios.html')


@Administrador_bp.route('/asignaturas')
def asignaturas():
    return render_template('Administrador/Asignaturas.html')


@Administrador_bp.route('/horarios')
def horarios():
    return render_template('Administrador/Horarios.html')


@Administrador_bp.route('/registro_notas/<int:curso_id>')
def registro_notas(curso_id):
    return render_template('Administrador/RegistroNotas.html', curso_id=curso_id)


@Administrador_bp.route('/notas_curso/<int:curso_id>')
def notas_curso(curso_id):
    return render_template("Administrador/notas_curso.html", curso_id=curso_id)


@Administrador_bp.route('/notas_registro')
def notas_registro():
    return render_template('Administrador/Notas_Registro.html')

@Administrador_bp.route('/notas_consultar')
def notas_consultar():
    return render_template('Administrador/Notas_Consultar.html')

@Administrador_bp.route('/observador')
def observador():
    return render_template('Administrador/Observador.html')

@Administrador_bp.route('/calculo_promedio')
def calculo_promedio():
    return render_template('Administrador/CalculoPromedio.html')

@Administrador_bp.route('/crear_encuesta')
def crear_encuesta():
    return render_template('Administrador/CrearEncuesta.html')

@Administrador_bp.route('/editar_eliminar_encuesta')
def editar_eliminar_encuesta():
    return render_template('Administrador/EditarEliminarEncuesta.html')

@Administrador_bp.route('/resultados_encuesta')
def resultados_encuesta():
    return render_template('Administrador/ResultadosEncuesta.html')

@Administrador_bp.route('/ver_promedio')
def ver_promedio():
    return render_template('Administrador/VerPromedio.html')

@Administrador_bp.route('/configuracion_academica')
def configuracion_academica():
    return render_template('Administrador/ConfiguracionAcademica.html')


@Administrador_bp.route('/repitentes')
@login_required
def repitentes():
    """
    Lista estudiantes repitentes (más de una matrícula en distintos años lectivos).
    """
    repitentes = (
        db.session.query(
            Usuario.ID_Usuario,
            Usuario.Nombre,
            Usuario.Apellido,
            Usuario.TipoDocumento,
            Usuario.NumeroDocumento,
            func.count(Matricula.AnioLectivo).label("VecesMatriculado")
        )
        .join(Matricula, Usuario.ID_Usuario == Matricula.ID_Estudiante)
        .filter(Usuario.Rol == 'Estudiante')
        .group_by(
            Usuario.ID_Usuario,
            Usuario.Nombre,
            Usuario.Apellido,
            Usuario.TipoDocumento,
            Usuario.NumeroDocumento
        )
        .having(func.count(Matricula.AnioLectivo) > 1)
        .order_by(func.count(Matricula.AnioLectivo).desc())
        .all()
    )

    return render_template('Administrador/Repitentes.html', repitentes=repitentes)

@Administrador_bp.route('/repitentes2/<int:id_estudiante>')
@login_required
def historial_repitente(id_estudiante):
    estudiante = Usuario.query.get_or_404(id_estudiante)

    # buscamos todas sus matrículas
    historial = db.session.query(
        Matricula.AnioLectivo,
        Curso.Grado.label("Curso"),
        db.func.avg(Actividad.Calificacion).label("Promedio")
    ).join(Curso, Curso.ID_Matricula == Matricula.ID_Matricula) \
     .join(Actividad, Actividad.ID_Matricula == Matricula.ID_Matricula) \
     .filter(Matricula.ID_Estudiante == id_estudiante) \
     .group_by(Matricula.AnioLectivo, Curso.Grado) \
     .order_by(Matricula.AnioLectivo.asc()) \
     .all()

    # contar cuántas veces se matriculó
    veces = Matricula.query.filter_by(ID_Estudiante=id_estudiante).count()

    # último curso (curso actual)
    curso_actual = historial[-1].Curso if historial else "N/A"

    return render_template(
        'Administrador/historial_repitente.html',
        estudiante=estudiante,
        historial=historial,
        curso_actual=curso_actual,
        veces=veces
    )

@Administrador_bp.route('/cursos')
def cursos():
    return render_template('Administrador/Cursos.html', cursos=cursos)

@Administrador_bp.route('/historialacademico')
def historialacademico():
    return render_template('Administrador/HistorialAcademico.html')

# ----------------- SUB-PÁGINAS -----------------
@Administrador_bp.route('/registrotutorias2')
def registrotutorias2():
    return render_template('Administrador/RegistroTutorías2.html')

@Administrador_bp.route('/cursos2', methods=['GET', 'POST'])
def cursos2():
    if request.method == 'POST':
        grado = request.form['Grado']
        grupo = request.form['Grupo']
        anio = request.form['Anio']
        director = request.form['DirectorGrupo']

        nuevo_curso = Curso(
            Grado=grado,
            Grupo=grupo,
            Anio=anio,
            Estado="Activo",
            DirectorGrupo=director if director else None
        )
        db.session.add(nuevo_curso)
        db.session.commit()
        flash("✅ Curso agregado correctamente", "success")

        return redirect(url_for('Administrador.cursos2'))

    # 👇 para GET (mostrar cursos)
    cursos = Curso.query.all()
    usuarios = Usuario.query.all()
    return render_template('Administrador/Cursos2.html', cursos=cursos, usuarios=usuarios)

@Administrador_bp.route('/agregar_curso', methods=['POST'])
@login_required
def agregar_curso():
    grado = request.form['grado']
    grupo = request.form['grupo']
    anio = request.form['anio']
    director_id = request.form['director']

    # Aquí guardas en la BD
    nuevo_curso = Curso(
        grado=grado,
        grupo=grupo,
        anio=anio,
        director_id=director_id
    )
    db.session.add(nuevo_curso)
    db.session.commit()

    flash("Curso agregado exitosamente", "success")
    return redirect(url_for('Administrador.cursos2'))


@Administrador_bp.route('/citacion')
def citacion():
    return render_template('Administrador/Citacion.html')

@Administrador_bp.route('/materias')
def materias():
    return render_template('Administrador/Materias.html')

@Administrador_bp.route('/inasistencias')
def inasistencias():
    return render_template('Administrador/inasistencias.html')

@Administrador_bp.route('/reporte')
def reporte():
    return render_template('Administrador/Reporte.html')


@Administrador_bp.route('/detallesmateria/<int:curso_id>')
def detallesmateria(curso_id):
    materias = {
        601: "Español",
        602: "Matemáticas",
        603: "Inglés",
        701: "Sociales",
        702: "Ética",
        703: "Filosofía",
        801: "Artística",
        802: "Biología",
        803: "Física",
        901: "Química",
        902: "Religión",
        903: "Tecnología",
        1001: "Informática",
        1002: "P.T.I",
        1003: "Ruta",
        1101: "Educación Física"
    }

    materia_nombre = materias.get(curso_id, "Materia desconocida")
    return render_template("Administrador/DetallesMateria.html", materia=materia_nombre)

@Administrador_bp.route('/enviar_correo', methods=['GET', 'POST'])
@login_required
def enviar_correo():
    if request.method == 'POST':
        from app import mail  # ✅ Importación local, evita circular import

        curso = request.form.get('curso')
        tipo = request.form.get('tipo')
        destinatario = request.form.get('destinatario')
        archivo = request.files.get('archivo')

        if not destinatario or not archivo:
            flash("Faltan datos ❌", "danger")
            return redirect(url_for('Administrador.paginainicio'))

        try:
            msg = Message(
                subject=f"{tipo} - Curso {curso}",
                recipients=[destinatario]
            )

            # 📌 Plantilla HTML bonita
            msg.html = render_template(
                "Administrador/CorreoAdjunto.html",
                curso=curso,
                tipo=tipo,
                destinatario=destinatario
            )

            # 📎 Adjuntar archivo
            msg.attach(
                archivo.filename,
                archivo.content_type,
                archivo.read()
            )

            mail.send(msg)
            flash("Correo enviado correctamente ✅", "success")
        except Exception as e:
            flash(f"Error al enviar el correo: {e}", "danger")

        return redirect(url_for('Administrador.paginainicio'))

    # Si es GET, muestra el formulario
    return render_template("Administrador/Comunicaciòn.html")





@Administrador_bp.route('/asistencia')
def asistencia():
    return render_template('Administrador/Asistencia.html')

@Administrador_bp.route('/historialacademico2')
def historialacademico2():
    return render_template('Administrador/HistorialAcademico2.html')

@Administrador_bp.route('/historialacademico3')
def historialacademico3():
    periodo = request.args.get('periodo')
    return render_template('Administrador/HistorialAcademico3.html', periodo=periodo)
