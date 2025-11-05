from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import generate_password_hash
from sqlalchemy import func
from datetime import datetime, date
from Controladores.models import db, Usuario, Matricula, Curso, Periodo, Asignatura, Docente_Asignatura, Programacion, Cronograma_Actividades, Actividad, Observacion, Bloques
from flask_mail import Message
import sys
import os


from decimal import Decimal


sys.stdout.reconfigure(encoding='utf-8')
#Definir el Blueprint para el administardor
Administrador_bp = Blueprint('Administrador', __name__, url_prefix='/administrador')


# ----------------- RUTAS DE INICIO -----------------
@Administrador_bp.route('/paginainicio')
def paginainicio():
    return render_template('Administrador/Paginainicio_Administrador.html')

# ----------------- DOCENTES -----------------
@Administrador_bp.route('/profesores')
@login_required
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
        tipo_doc = request.form['TipoDocumento']
        profesion = request.form['Profesion']
        ciclo = request.form['Ciclo']

        # contraseña por defecto
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
            Direccion=profesion,
            Genero="Otro"
        )

        
        nuevo_docente.Calle = ciclo

        db.session.add(nuevo_docente)
        db.session.commit()
        flash("✅ Docente agregado correctamente", "success")

    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f"❌ Error al agregar docente: {str(e)}", "danger")

    return redirect(url_for('Administrador.profesores'))


@Administrador_bp.route('/actualizar_docente/<int:id>', methods=['POST'])
@login_required
def actualizar_docente(id):
    docente = Usuario.query.get_or_404(id)

    try:
        docente.Nombre = request.form['Nombre']
        docente.Apellido = request.form['Apellido']
        docente.TipoDocumento = request.form['TipoDocumento']
        docente.NumeroDocumento = request.form['NumeroDocumento']
        docente.Correo = request.form['Correo']
        docente.Telefono = request.form['Telefono']
        docente.Direccion = request.form['Profesion']  # profesión
        docente.Calle = request.form['Ciclo']          # ciclo

        db.session.commit()
        flash("✅ Docente actualizado correctamente.", "success")

    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f"❌ Error al actualizar docente: {str(e)}", "danger")

    return redirect(url_for('Administrador.profesores'))


@Administrador_bp.route('/eliminar_docente/<int:id>', methods=['POST'])
@login_required
def eliminar_docente(id):
    docente = Usuario.query.get_or_404(id)

    try:
        db.session.delete(docente)
        db.session.commit()
        flash("🗑️ Docente eliminado correctamente", "danger")
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f"❌ Error al eliminar docente: {str(e)}", "danger")

    return redirect(url_for('Administrador.profesores'))


# ----------------- ESTUDIANTES -----------------
@Administrador_bp.route('/estudiantes')
@login_required
def estudiantes():
    estudiantes = Usuario.query.filter_by(Rol='Estudiante').all()
    cursos = Curso.query.filter_by(Estado='Activo').all()
    return render_template('Administrador/Estudiantes.html', estudiantes=estudiantes, cursos=cursos)


@Administrador_bp.route('/agregar_estudiante', methods=['POST'])
def agregar_estudiante():
    try:
        nombre = request.form['Nombre']
        apellido = request.form['Apellido']
        tipo_documento = request.form['TipoDocumento']
        numero_documento = request.form['NumeroDocumento']
        correo = request.form['Correo']
        telefono = request.form['Telefono']
        direccion = request.form['Direccion']

        # 🔒 Generar una contraseña por defecto (puedes cambiar la lógica si quieres)
        contrasena_plana = numero_documento  # o podrías usar una aleatoria
        contrasena_hash = generate_password_hash(contrasena_plana, method='pbkdf2:sha256')

        # Crear el nuevo usuario
        nuevo_estudiante = Usuario(
            Rol='Estudiante',
            Nombre=nombre,
            Apellido=apellido,
            TipoDocumento=tipo_documento,
            NumeroDocumento=numero_documento,
            Correo=correo,
            Telefono=telefono,
            Direccion=direccion,
            Contrasena=contrasena_hash
        )

        db.session.add(nuevo_estudiante)
        db.session.commit()

        print(f"✅ Estudiante registrado correctamente: {nombre} {apellido}")
        return jsonify({'success': True, 'id_estudiante': nuevo_estudiante.ID_Usuario})

    except Exception as e:
            print("❌ Error al registrar estudiante:", e)
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)})
    
@Administrador_bp.route('/agregar_matricula', methods=['POST'])
def agregar_matricula():
    try:
        nueva_matricula = Matricula(
            ID_Estudiante=request.form['ID_Estudiante'],
            ID_Curso=request.form['ID_Curso'],
            Correo=request.form['Correo'],
            FechaNacimiento=request.form['FechaNacimiento'],
            DepNacimiento=request.form.get('DepNacimiento'),
            TipoDocumento=request.form['TipoDocumento'],
            NumeroDocumento=request.form['NumeroDocumento'],
            AnioLectivo=request.form['AnioLectivo']
        )

        db.session.add(nueva_matricula)
        db.session.commit()

        flash("✅ Matrícula registrada correctamente", "success")
        return redirect(url_for('Administrador.estudiantes'))

    except Exception as e:
        db.session.rollback()
        print("❌ Error al registrar matrícula:", e)
        flash("Error al registrar matrícula", "danger")
        return redirect(url_for('Administrador.estudiantes'))


@Administrador_bp.route('/actualizar_estudiante/<int:id>', methods=['POST'])
@login_required
def actualizar_estudiante(id):
    estudiante = Usuario.query.get_or_404(id)
    try:
        estudiante.Nombre = request.form['Nombre']
        estudiante.Apellido = request.form['Apellido']
        estudiante.TipoDocumento = request.form['TipoDocumento']
        estudiante.NumeroDocumento = request.form['NumeroDocumento']
        estudiante.Correo = request.form['Correo']
        estudiante.Telefono = request.form['Telefono']
        estudiante.Direccion = request.form['Direccion']
        db.session.commit()
        flash("✅ Estudiante actualizado correctamente", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"❌ Error al actualizar: {e}", "danger")

    return redirect(url_for('Administrador.estudiantes'))


@Administrador_bp.route('/eliminar_estudiante/<int:id>', methods=['POST'])
@login_required
def eliminar_estudiante(id):
    estudiante = Usuario.query.get_or_404(id)
    try:
        db.session.delete(estudiante)
        db.session.commit()
        flash("🗑️ Estudiante eliminado correctamente", "danger")
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f"❌ Error al eliminar estudiante: {str(e)}", "danger")

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

@Administrador_bp.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        # --- Imprime lo que llega (diagnóstico) ---
        print("==== /administrador/registro POST recibido ====")
        print("request.form:", request.form)
        print("request.files:", request.files)

        nombre = request.form.get('Nombre')
        apellido = request.form.get('Apellido')
        correo = request.form.get('Correo')
        contrasena = request.form.get('Contrasena')
        confirmar = request.form.get('ConfirmarContrasena') or request.form.get('Confirmar')  # por si el campo se llama distinto
        numero_documento = request.form.get('NumeroDocumento')
        telefono = request.form.get('Telefono')
        direccion = request.form.get('Direccion')
        rol = request.form.get('Rol')

        tipo_documento = request.form.get('TipoDocumento', 'CC')
        estado = request.form.get('Estado', 'Activo')
        genero = request.form.get('Genero', '')

        # Validaciones básicas
        if not all([nombre, apellido, correo, contrasena, numero_documento, telefono, direccion, rol]):
            flash('Por favor, completa todos los campos requeridos.', 'warning')
            return redirect(url_for('Administrador.registro'))

        # Validar confirmación de contraseña (si existe campo confirmar)
        if confirmar is not None and contrasena != confirmar:
            flash('Las contraseñas no coinciden.', 'warning')
            return redirect(url_for('Administrador.registro'))

        try:
            # Verificar si ya existe el correo
            existing_user = Usuario.query.filter_by(Correo=correo).first()
            if existing_user:
                flash('El correo ya está registrado.', 'warning')
                return redirect(url_for('Administrador.registro'))

            # Hashear contraseña
            hashed_password = generate_password_hash(contrasena)

            # Crear el usuario
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

            print("-> Usuario registrado: ", correo)
            flash('Usuario registrado correctamente ✅', 'success')
            return redirect(url_for('Administrador.registro'))

        except SQLAlchemyError as e:
            db.session.rollback()
            # muestra el error en consola para depurar
            import traceback
            traceback.print_exc()
            flash(f'Error al registrar (SQLAlchemy): {str(e)}', 'danger')
            return redirect(url_for('Administrador.registro'))
        except Exception as e:
            db.session.rollback()
            import traceback
            traceback.print_exc()
            flash(f'Error inesperado al registrar: {str(e)}', 'danger')
            return redirect(url_for('Administrador.registro'))

    # GET → render
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


#----------------------parte de horarios-------------------
@Administrador_bp.route('/horarios', defaults={'curso_id': None})
@Administrador_bp.route('/horarios/<int:curso_id>')
def horarios(curso_id):
    if curso_id is None:
        return redirect(url_for('Administrador.ver_horarios'))

    c = Curso.query.get(curso_id)
    if not c:
        return "Curso no encontrado", 404

    asignaciones = Docente_Asignatura.query.filter_by(ID_Curso=curso_id).all()

    return render_template(
        'Administrador/Horarios.html',
        curso=c,
        asignaciones=asignaciones
    )
    
@Administrador_bp.route('/ver_horarios')
def ver_horarios():
    # traer todos los cursos activos
    cursos = Curso.query.filter_by(Estado='Activo').all()

    # armar diccionario de ciclos
    ciclos = {
        1: [],
        2: [],
        3: []
    }

    for c in cursos:
        g = int(c.Grado)
        if g in (6,7):
            ciclos[1].append(c)
        elif g in (8,9):
            ciclos[2].append(c)
        elif g in (10,11):
            ciclos[3].append(c)

    return render_template("Administrador/VerHorarios.html", ciclos=ciclos)

@Administrador_bp.route('/guardar_horario/<int:curso_id>', methods=['POST'])
def guardar_horario(curso_id):
    try:
        payload = request.get_json()
        if isinstance(payload, dict) and 'bloques' in payload:
            bloques = payload['bloques']
        elif isinstance(payload, list):
            bloques = payload
        else:
            return jsonify({"ok": False, "error": "payload inválido"}), 400

        from datetime import datetime, timedelta

        dia_map = {
            'lun': 'Lunes', 'mar': 'Martes', 'mie': 'Miércoles',
            'jue': 'Jueves', 'vie': 'Viernes',
            'Lunes': 'Lunes', 'Martes': 'Martes', 'Miércoles': 'Miércoles',
            'Jueves': 'Jueves', 'Viernes': 'Viernes'
        }

        # Eliminar programaciones previas del curso
        Programacion.query.filter_by(ID_Curso=curso_id).delete()
        db.session.flush()

        for b in bloques:
            # normalizar día
            raw_dia = b.get('dia')
            dia = dia_map.get(str(raw_dia), str(raw_dia)).strip() if raw_dia else None

            raw_hora = b.get('hora') or b.get('hora_inicio') or b.get('horaInicio')
            if not raw_hora:
                # si no hay hora, se salta
                continue
            hora_str = str(raw_hora).strip()

            try:
                hora_inicio = datetime.strptime(hora_str, "%H:%M").time()
            except Exception:
                # si no cumple formato, saltar
                print("Formato hora inválido:", hora_str)
                continue

            raw_hora_fin = b.get('hora_fin') or b.get('horaFin')
            if raw_hora_fin:
                try:
                    hora_fin = datetime.strptime(str(raw_hora_fin).strip(), "%H:%M").time()
                except Exception:
                    hora_fin = (datetime.combine(datetime.today(), hora_inicio) + timedelta(hours=1)).time()
            else:
                hora_fin = (datetime.combine(datetime.today(), hora_inicio) + timedelta(hours=1)).time()

            # buscar asignación por id ó por materia+docente
            asignacion = None
            id_da = b.get('id') or b.get('id_da') or b.get('id_docente_asignatura') or b.get('ID_Docente_Asignatura')
            if id_da:
                asignacion = Docente_Asignatura.query.get(int(id_da))

            if not asignacion:
                materia = (b.get('materia') or '').strip()
                docente = (b.get('docente') or '').strip()
                if not materia or not docente:
                    print("Falta materia o docente en bloque:", b)
                    continue

                asignacion = Docente_Asignatura.query.join(Docente_Asignatura.asignatura)\
                    .join(Docente_Asignatura.docente)\
                    .filter(
                        Asignatura.Nombre == materia,
                        Usuario.Nombre == docente,
                        Docente_Asignatura.ID_Curso == curso_id
                    ).first()

            if not asignacion:
                print(f"No se encontró asignación para {b.get('materia')} - {b.get('docente')} (curso {curso_id})")
                continue

            # validar ID_Bloque: si viene, comprobar que exista en la tabla Bloques
            id_bloque = b.get('id_bloque') or b.get('ID_Bloque')
            id_bloque_valid = None
            if id_bloque:
                try:
                    # intenta convertir y buscar
                    id_b = int(id_bloque)
                    bloque_obj = Bloques.query.get(id_b)
                    if bloque_obj:
                        id_bloque_valid = id_b
                except Exception:
                    id_bloque_valid = None

            # crear programacion
            prog = Programacion(
                ID_Curso=curso_id,
                ID_Docente_Asignatura=asignacion.ID_Docente_Asignatura,
                ID_Docente=asignacion.ID_Docente,
                Dia=dia,
                HoraInicio=hora_inicio,
                HoraFin=hora_fin,
                ID_Bloque=id_bloque_valid
            )
            db.session.add(prog)

        db.session.commit()
        print("✅ Horario guardado correctamente.")
        return jsonify({"ok": True}), 200

    except Exception as e:
        db.session.rollback()
        print("❌ ERROR guardar_horario:", e)
        return jsonify({"ok": False, "error": str(e)}), 500    
    
@Administrador_bp.route('/api/curso/<int:id_curso>/programacion')
def api_programacion(id_curso):
    c = Curso.query.get(id_curso)
    if not c:
        return jsonify({"error": "Curso no existe"}), 404

    programaciones = Programacion.query.filter_by(ID_Curso=id_curso).all()
    data = []

    for p in programaciones:
        data.append({
            "ID_Docente_Asignatura": p.ID_Docente_Asignatura,
            "materia": p.docente_asignatura.asignatura.Nombre,
            "docente": p.docente_asignatura.docente.Nombre,
            "Dia": p.Dia,
            "Hora": str(p.HoraInicio)  # o un índice de bloque
        })

    return jsonify({"programacion": data}), 200

@Administrador_bp.route('/api/curso/<int:id_curso>/asignaciones')
def api_asignaciones(id_curso):
    asignaciones = Docente_Asignatura.query.filter_by(ID_Curso=id_curso).all()
    data = []

    for a in asignaciones:
        data.append({
            "id": a.ID_Docente_Asignatura,
            "texto": f"{a.asignatura.Nombre} - {a.docente.Nombre}"
        })

    return jsonify(data), 200


@Administrador_bp.route('/api/curso/<int:id_curso>/bloques_db')
def api_bloques_db(id_curso):

    def dia_to_short(dia):
        mapa = {
            "Lunes": "lun",
            "Martes": "mar",
            "Miércoles": "mie",
            "Jueves": "jue",
            "Viernes": "vie"
        }
        return mapa.get(dia, None)

    def hora_to_bloque(hora):
        mapa = {
            "06:45": 0,
            "07:30": 1,
            "08:00": 1,
            "08:30": 2,
            "09:00": 2,
            "09:50": 3,
            "10:00": 3,
            "10:40": 4,
            "11:30": 5,
            "13:30": 6,
            "14:20": 7
        }
        return mapa.get(hora, None)

    programaciones = Programacion.query.filter_by(ID_Curso=id_curso).all()
    data = []

    for p in programaciones:
        inicio = p.HoraInicio.strftime('%H:%M') if p.HoraInicio else None

        data.append({
            "id": p.ID_Programacion,
            "materia": p.docente_asignatura.asignatura.Nombre,
            "docente": p.docente_asignatura.docente.Nombre,
            "dia": dia_to_short(p.Dia),
            "hora": hora_to_bloque(inicio),
        })

    return jsonify(data), 200


@Administrador_bp.route('/api/curso/<int:id_curso>/bloques')
def api_bloques(id_curso):
    asignaciones = Docente_Asignatura.query.filter_by(ID_Curso=id_curso).all()

    data = []
    for a in asignaciones:
        data.append({
            "id_da": a.ID_Docente_Asignatura,
            "materia": a.asignatura.Nombre,
            "docente": a.docente.Nombre
        })

    return jsonify(data), 200

@Administrador_bp.route('/api/curso/<int:id_curso>/num_bloques')
def api_num_bloques(id_curso):
    total = Programacion.query.filter_by(ID_Curso=id_curso).count()
    return jsonify({"bloques": total}), 200

@Administrador_bp.route('/obtener_programacion', methods=['GET'])
def obtener_programacion():
    try:
        programaciones = Programacion.query.all()
        data = []
        for p in programaciones:
            data.append({
                "curso_id": p.ID_Curso,
                "docente_asignatura_id": p.ID_Docente_Asignatura,
                "dia": p.Dia,
                "hora_inicio": p.HoraInicio.strftime('%H:%M') if p.HoraInicio else None,
                "hora_fin": p.HoraFin.strftime('%H:%M') if p.HoraFin else None
            })

        return jsonify(data), 200

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"status": "error", "msg": str(e)}), 500
    
@Administrador_bp.route('/api/curso/<int:curso_id>/bloques_db')
def bloques_db(curso_id):
    try:
        programaciones = Programacion.query.join(Docente_Asignatura).join(Asignatura).join(Usuario).filter(
            Programacion.ID_Curso == curso_id
        ).all()

        data = []
        for p in programaciones:
            # preferir hora desde la tabla Bloques si ID_Bloque está presente y tiene HoraInicio
            hora_inicio = None
            if p.ID_Bloque and getattr(p, 'bloques', None):
                try:
                    hora_inicio = p.bloques.HoraInicio.strftime("%H:%M")
                except Exception:
                    hora_inicio = p.HoraInicio.strftime("%H:%M") if p.HoraInicio else None
            else:
                hora_inicio = p.HoraInicio.strftime("%H:%M") if p.HoraInicio else None

            data.append({
                "id": p.ID_Programacion,
                "id_bloque": p.ID_Bloque,
                "dia": p.Dia,
                "hora_inicio": hora_inicio,
                "hora_fin": p.HoraFin.strftime("%H:%M") if p.HoraFin else None,
                "materia": p.docente_asignatura.asignatura.Nombre if p.docente_asignatura.asignatura else "",
                "docente": p.docente_asignatura.docente.Nombre if p.docente_asignatura.docente else ""
            })

        return jsonify(data), 200

    except Exception as e:
        print("Error al cargar bloques:", e)
        return jsonify({"status": "error", "msg": str(e)}), 500
#----------------------------------------------------------------------------

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

# GESTIÓN DE LA OBSERVACIÓN #

@Administrador_bp.route('/observador')
def observador():
    observaciones = (
        db.session.query(Observacion, Usuario)
        .join(Matricula, Observacion.ID_Matricula == Matricula.ID_Matricula)
        .join(Usuario, Matricula.ID_Estudiante == Usuario.ID_Usuario)
        .all()
    )

    estudiantes = Usuario.query.filter_by(Rol='Estudiante').all()

    return render_template(
        'Administrador/Observador.html',
        observaciones=observaciones,
        estudiantes=estudiantes
    )


@Administrador_bp.route('/observador/registrar', methods=['POST'])
def registrar_observacion():
    data = request.form

    id_estudiante = data.get('id_estudiante')
    if not id_estudiante:
        return jsonify({"status": "error", "message": "Debe seleccionar un estudiante"}), 400

    # Buscar matrícula del estudiante
    matricula = Matricula.query.filter_by(ID_Estudiante=id_estudiante).first()
    if not matricula:
        return jsonify({"status": "error", "message": "El estudiante no tiene matrícula asignada"}), 400

    # Buscar horario según la matrícula
    horario = Programacion.query.filter_by(ID_Curso=matricula.ID_Curso).first()
    if not horario:
        return jsonify({"status": "error", "message": "No hay horario asociado al estudiante"}), 400
    
    nueva_obs = Observacion(
        Fecha=datetime.strptime(data.get('fecha'), "%Y-%m-%d").date(),
        Descripcion=data.get('descripcion'),
        Tipo=data.get('tipo'),
        NivelImportancia=data.get('nivelImportancia'),
        Recomendacion=data.get('recomendacion'),
        Estado='Activa',
        ID_Horario=horario.ID_Programacion,
        ID_Matricula=matricula.ID_Matricula,
        ID_Estudiante=id_estudiante
    )

    try:
        db.session.add(nueva_obs)
        db.session.commit()
        return jsonify({"status": "ok", "message": "Observación registrada correctamente"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": f"Error al guardar: {str(e)}"}), 500


@Administrador_bp.route('/calculo_promedio')
def calculo_promedio():
    return render_template('Administrador/CalculoPromedio.html')

@Administrador_bp.route('/encuesta')
def encuesta():
    return render_template('Administrador/Encuestas.html')

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
    ).join(Curso, Curso.ID_Curso == Matricula.ID_Curso) \
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
    cursos = Curso.query.all()
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

    # para GET (mostrar cursos)
    cursos = Curso.query.all()
    usuarios = Usuario.query.all()
    return render_template('Administrador/Cursos2.html', cursos=cursos, usuarios=usuarios)

@Administrador_bp.route('/agregar_curso', methods=['POST'])
def agregar_curso():
    try:
        grado = request.form['Grado']
        grupo = request.form['Grupo']
        anio = request.form['Anio']
        estado = request.form['Estado']
        director = request.form['DirectorGrupo']

        nuevo_curso = Curso(
            Grado=grado,
            Grupo=grupo,
            Anio=anio,
            Estado=estado,
            DirectorGrupo=director
        )

        db.session.add(nuevo_curso)
        db.session.commit()

        flash('Curso agregado exitosamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al agregar el curso: {e}', 'danger')

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

    # Obtener la materia según el curso (si existe)
    materia = materias.get(curso_id, "Materia no encontrada")

    # Enviar curso y materia al HTML
    return render_template('Administrador/detallesmateria.html', curso=curso_id, materia=materia)


    materia_nombre = materias.get(curso_id, "Materia desconocida")   
    return render_template("Administrador/DetallesMateria.html", materia=materia_nombre)
 
@Administrador_bp.route('/enviar_correo', methods=['GET', 'POST'])
@login_required
def enviar_correo():
    if request.method == 'POST':

        from app import mail  


        curso = request.form.get('curso')
        tipo = request.form.get('tipo')
        destinatario = request.form.get('destinatario') or request.form.get('emailDestino')
        archivo = request.files.get('archivo')

        print("➡ /enviar_correo llamado")
        print("   curso:", curso, "tipo:", tipo, "destinatario:", destinatario)
        print("   archivo:", getattr(archivo, 'filename', None))

        if not destinatario:
            flash("Falta el correo del destinatario.", "danger")
            return redirect(url_for('Administrador.comunicacion'))

        try:
            msg = Message(
                subject=f"{tipo or 'Sin tipo'} - Curso {curso or 'N/A'}",
                recipients=[destinatario],
            )

            try:
                msg.html = render_template(
                    "Administrador/CorreoAdjunto.html",
                    curso=curso,
                    tipo=tipo,
                    destinatario=destinatario
                )
            except Exception as tpl_err:
                print("Error renderizando template:", tpl_err)
                msg.body = f"Envío: {tipo} - Curso {curso}"

            if archivo and archivo.filename:
        
                data = archivo.read()
                print(f"   tamaño adjunto: {len(data)} bytes")
       
                msg.attach(archivo.filename, archivo.content_type or 'application/octet-stream', data)
            else:
                print("   No se adjuntó archivo")

            mail.send(msg)
            flash("Correo enviado correctamente ✅", "success")
            print("✔ mail enviado a", destinatario)

        except Exception as e:
   
            import traceback
            traceback.print_exc()
            flash(f"Error al enviar el correo: {e}", "danger")

        return redirect(url_for('Administrador.comunicacion'))

  
    return render_template("Administrador/Comunicacion.html")


@Administrador_bp.route('/asistencia')
def asistencia():
    return render_template('Administrador/Asistencia.html')

@Administrador_bp.route('/historialacademico2')
def historialacademico2():
    return render_template('Administrador/HistorialAcademico2.html')

@Administrador_bp.route('/evaluaciones')
def evaluaciones():
    return render_template('Administrador/evaluaciones.html')

@Administrador_bp.route('/informe')
def informe():
    return render_template('Administrador/informe.html')

@Administrador_bp.route('/historialacademico3')
def historialacademico3():
    periodo = request.args.get('periodo')
    return render_template('Administrador/HistorialAcademico3.html', periodo=periodo)

@Administrador_bp.route('/configuracion_academica2')
def configuracion_academica2():
    return render_template('Administrador/ConfiguracionAcademica2.html')

@Administrador_bp.route('/configuracion_academica3')
def configuracion_academica3():
    return render_template('Administrador/ConfiguracionAcademica3.html')

@Administrador_bp.route('/comunicacion2')
def comunicacion2():
    return render_template('Administrador/Comunicación2.html')
