from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session, current_app
from flask_login import login_required, current_user
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func
from sqlalchemy import func, and_, or_, extract
from sqlalchemy import or_, text
from datetime import datetime
from Controladores.models import db, Usuario, Matricula, Nota_Calificaciones, Reporte_Notas, Curso, Periodo, Asignatura, Docente_Asignatura, Programacion, Cronograma_Actividades, Observacion, Bloques, Reuniones, Tutorias, Noticias, ResumenSemanal, Citaciones, Acudiente, Notificacion, Estudiantes_Repitentes, Detalle_Asistencia, Asistencia, Encuesta, Encuesta_Pregunta, Encuesta_Respuesta, Historial_Academico
from flask_mail import Message
import sys
import os
from werkzeug.utils import secure_filename



from decimal import Decimal


sys.stdout.reconfigure(encoding='utf-8')
#Definir el Blueprint para el administardor
Administrador_bp = Blueprint('Administrador', __name__, url_prefix='/administrador')


# ----------------- RUTAS DE INICIO -----------------
@Administrador_bp.route('/paginainicio')
def paginainicio():
    return render_template('Administrador/Paginainicio_Administrador.html')

# ---------------- CONSULTA DE NOTAS (ADMINISTRADOR) ----------------
@Administrador_bp.route('/notas_curso')
@Administrador_bp.route('/notas_curso/<int:curso_id>')
def notas_curso(curso_id=None):
    return render_template('Administrador/notas_curso.html', curso_id=curso_id)

@Administrador_bp.route('/cursos/lista', methods=['GET'])
def lista_cursos_activos():
    cursos = Curso.query.filter_by(Estado='Activo').order_by(Curso.Grado, Curso.Grupo).all()
    data = [
        {
            "id": c.ID_Curso,
            "grado": getattr(c, 'Grado', None),
            "grupo": getattr(c, 'Grupo', None),
            "nombre": f"{getattr(c,'Grado', '')}-{getattr(c,'Grupo','')}".strip('-')
        }
        for c in cursos
    ]
    return jsonify({"success": True, "cursos": data})

@Administrador_bp.route('/asignaturas/lista', methods=['GET'])
def lista_asignaturas():
    # Opcional: filtrar por curso_id para evitar duplicados y mostrar solo asignaturas del curso
    curso_id = request.args.get('curso_id', type=int)
    try:
        # Traer todas las asignaturas disponibles (base)
        todas_asign = Asignatura.query.order_by(Asignatura.Nombre).all()

        prioritarias = set()
        if curso_id:
            # Intentar mapear curso_id tipo 1101 -> ID_Curso real si es necesario
            sub_base = db.session.query(Matricula.ID_Estudiante).filter(Matricula.ID_Curso == curso_id)
            if sub_base.count() == 0 and isinstance(curso_id, int) and curso_id >= 100:
                grado_calc = curso_id // 100
                grupo_calc = curso_id % 100
                grupo_candidatos = [str(grupo_calc), f"{grupo_calc:02d}"]
                letra_map = {1: 'A', 2: 'B', 3: 'C', 4: 'D', 5: 'E'}
                if grupo_calc in letra_map:
                    grupo_candidatos.append(letra_map[grupo_calc])
                curso_alt = None
                for g in grupo_candidatos:
                    curso_alt = Curso.query.filter(
                        or_(Curso.Grado == str(grado_calc), Curso.Grado == grado_calc),
                        or_(Curso.Grupo == g, Curso.Grupo == int(g)) if g.isdigit() else (Curso.Grupo == g)
                    ).first()
                    if curso_alt:
                        break
                if curso_alt:
                    curso_id = curso_alt.ID_Curso

            # Asignaturas con notas en el curso (para priorizar en la lista)
            subquery_est = db.session.query(Matricula.ID_Estudiante).filter(Matricula.ID_Curso == curso_id).subquery()
            asign_ids_rows = db.session.query(Nota_Calificaciones.ID_Asignatura).filter(Nota_Calificaciones.ID_Estudiante.in_(subquery_est)).distinct().all()
            prioritarias = {row[0] for row in asign_ids_rows}

        # Deduplicar por nombre y construir lista final
        vistos = set()
        lista = []
        for a in todas_asign:
            nombre = (a.Nombre or '').strip()
            key = nombre.lower()
            if key in vistos:
                continue
            vistos.add(key)
            lista.append({"id": a.ID_Asignatura, "nombre": nombre, "prioridad": 1 if a.ID_Asignatura in prioritarias else 0})

        # Orden: primero las que tienen datos para el curso, luego alfabético
        lista.sort(key=lambda x: (-x["prioridad"], x["nombre"]))

        # Quitar campo de prioridad antes de responder
        for item in lista:
            item.pop("prioridad", None)

        return jsonify({"success": True, "asignaturas": lista})
    except Exception as e:
        print('Error en /asignaturas/lista:', e)
        return jsonify({"success": False, "error": str(e)}), 500

@Administrador_bp.route('/notas', methods=['GET'])
def consultar_notas():
    try:
        curso_id = request.args.get('curso_id', type=int)
        asignatura_id = request.args.get('asignatura_id', type=int)
        periodo = request.args.get('periodo', type=int)

        if not curso_id or not asignatura_id or not periodo:
            return jsonify({"success": False, "error": "Parámetros requeridos: curso_id, asignatura_id, periodo"}), 400

        # Estudiantes matriculados en el curso (con fallback a grado+grupo si no coincide por ID)
        q_est = (
            db.session.query(Usuario, Matricula)
            .join(Matricula, Matricula.ID_Estudiante == Usuario.ID_Usuario)
            .filter(Matricula.ID_Curso == curso_id, Usuario.Rol == 'Estudiante')
            .order_by(Usuario.Apellido, Usuario.Nombre)
        )
        estudiantes_db = q_est.all()
        if len(estudiantes_db) == 0 and isinstance(curso_id, int) and curso_id >= 100:
            grado_calc = curso_id // 100
            grupo_calc = curso_id % 100
            grupo_candidatos = [str(grupo_calc), f"{grupo_calc:02d}"]
            letra_map = {1: 'A', 2: 'B', 3: 'C', 4: 'D', 5: 'E'}
            if grupo_calc in letra_map:
                grupo_candidatos.append(letra_map[grupo_calc])
            curso_alt = None
            for g in grupo_candidatos:
                curso_alt = Curso.query.filter(
                    or_(Curso.Grado == str(grado_calc), Curso.Grado == grado_calc),
                    or_(Curso.Grupo == g, Curso.Grupo == int(g)) if g.isdigit() else (Curso.Grupo == g)
                ).first()
                if curso_alt:
                    break
            if curso_alt:
                curso_id = curso_alt.ID_Curso
                estudiantes_db = (
                    db.session.query(Usuario, Matricula)
                    .join(Matricula, Matricula.ID_Estudiante == Usuario.ID_Usuario)
                    .filter(Matricula.ID_Curso == curso_id, Usuario.Rol == 'Estudiante')
                    .order_by(Usuario.Apellido, Usuario.Nombre)
                    .all()
                )
            else:
                # Último recurso: traer estudiantes por grado/grupo desde Curso join, si existe
                # Intentar por combinaciones de tipos
                for g in grupo_candidatos:
                    estudiantes_db = (
                        db.session.query(Usuario, Matricula)
                        .join(Matricula, Matricula.ID_Estudiante == Usuario.ID_Usuario)
                        .join(Curso, Curso.ID_Curso == Matricula.ID_Curso)
                        .filter(
                            or_(Curso.Grado == str(grado_calc), Curso.Grado == grado_calc),
                            (Curso.Grupo == g) if not g.isdigit() else or_(Curso.Grupo == g, Curso.Grupo == int(g)),
                            Usuario.Rol == 'Estudiante'
                        )
                        .order_by(Usuario.Apellido, Usuario.Nombre)
                        .all()
                    )
                    if estudiantes_db:
                        break

        # Notas para la asignatura y periodo
        notas_db = Nota_Calificaciones.query.filter_by(
            ID_Asignatura=asignatura_id,
            Periodo=periodo
        ).all()
        notas_por_estudiante = {n.ID_Estudiante: n for n in notas_db}

        resultados = []
        for usuario, _mat in estudiantes_db:
            reg = notas_por_estudiante.get(usuario.ID_Usuario)
            resultados.append({
                "estudiante_id": usuario.ID_Usuario,
                "apellido": usuario.Apellido,
                "nombre": usuario.Nombre,
                "nota_1": getattr(reg, 'Nota_1', None) if reg else None,
                "nota_2": getattr(reg, 'Nota_2', None) if reg else None,
                "nota_3": getattr(reg, 'Nota_3', None) if reg else None,
                "nota_4": getattr(reg, 'Nota_4', None) if reg else None,
                "nota_5": getattr(reg, 'Nota_5', None) if reg else None,
                "promedio_final": getattr(reg, 'Promedio_Final', None) if reg else None
            })

        return jsonify({"success": True, "notas": resultados})
    except Exception as e:
        print("Error en /administrador/notas:", e)
        return jsonify({"success": False, "error": str(e)}), 500


# ---------------- NOTIFICACIONES ADMINISTRADOR----------------





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
        genero = request.form['Genero']
        correo = request.form['Correo']
        telefono = request.form['Telefono']
        direccion = request.form['Direccion']
        contrasena = request.form['Contrasena']
        confirmar = request.form['ConfirmarContrasena']

        # Validación de contraseñas
        if contrasena != confirmar:
            return jsonify({'success': False, 'error': 'Las contraseñas no coinciden'})

        # Encriptar contraseña
        contrasena_hash = generate_password_hash(contrasena, method='pbkdf2:sha256')

        # Crear nuevo usuario estudiante
        nuevo_estudiante = Usuario(
            Rol='Estudiante',
            Nombre=nombre,
            Apellido=apellido,
            TipoDocumento=tipo_documento,
            NumeroDocumento=numero_documento,
            Genero=genero,
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
@Administrador_bp.route('/acudientes', methods=['GET'])
def acudientes():
    try:
        acudientes = db.session.query(
            Usuario.ID_Usuario,
            Usuario.Nombre,
            Usuario.Apellido,
            Usuario.TipoDocumento,
            Usuario.NumeroDocumento,
            Usuario.Correo,
            Usuario.Telefono,
            Usuario.Direccion,
            Acudiente.ID_Estudiante,
            Acudiente.Parentesco,
            Acudiente.Estado.label('estado_relacion')
        ).outerjoin(Acudiente, Usuario.ID_Usuario == Acudiente.ID_Usuario)\
         .filter(Usuario.Rol == 'Acudiente', Usuario.Estado == 'Activo').all()

        estudiantes = Usuario.query.filter_by(Rol='Estudiante', Estado='Activo').all()
        usuarios_acudientes = Usuario.query.filter_by(Rol='Acudiente', Estado='Activo').all()

        return render_template(
            'Administrador/acudientes.html',
            acudientes=acudientes,
            estudiantes=estudiantes,
            usuarios_acudientes=usuarios_acudientes
        )

    except Exception as e:
        print("⚠️ Error al cargar acudientes:", e)
        return render_template(
            'Administrador/acudientes.html',
            acudientes=[],
            estudiantes=[],
            usuarios_acudientes=[]
        )
    

# Registrar nuevo usuario acudiente
@Administrador_bp.route('/registrar_usuario_acudiente', methods=['POST'])
def registrar_usuario_acudiente():
    try:
        data = request.get_json() or request.form
        if not data:
            return jsonify({'message': '❌ No se recibieron datos JSON'}), 400

        print("📦 Datos recibidos del modal:", data)

        # Validación de campos requeridos
        campos_requeridos = ['Nombre', 'Apellido', 'TipoDocumento', 'NumeroDocumento', 'Correo', 'Contrasena', 'Genero']
        for campo in campos_requeridos:
            if not data.get(campo):
                return jsonify({'message': f'El campo {campo} es obligatorio.'}), 400
            
        if Usuario.query.filter_by(NumeroDocumento=data['NumeroDocumento']).first():
            return jsonify({'message': '⚠️ El número de documento ya está registrado.'}), 400
            
        if Usuario.query.filter_by(Correo=data['Correo']).first():
            return jsonify({'message': '⚠️ El correo ya está registrado.'}), 400
        
            # Validación de contraseñas
        contrasena = data['Contrasena']
        confirmar = data.get('ConfirmarContrasena')
        if contrasena != confirmar:
            return jsonify({'success': False, 'error': 'Las contraseñas no coinciden'}), 400

        # Encriptar contraseña
        contrasena_hash = generate_password_hash(contrasena, method='pbkdf2:sha256')

        # Crear el nuevo usuario acudiente
        nuevo_usuario = Usuario(
            Nombre=data['Nombre'],
            Apellido=data['Apellido'],
            TipoDocumento=data['TipoDocumento'],
            NumeroDocumento=data['NumeroDocumento'],
            Correo=data['Correo'],
            Contrasena=contrasena_hash,
            Telefono=data.get('Telefono'),
            Direccion=data.get('Direccion'),
            Genero=data.get('Genero'), 
            Rol='Acudiente',
            Estado='Activo'
        )

        db.session.add(nuevo_usuario)
        db.session.commit()

        return jsonify({
        'message': 'Acudiente registrado correctamente.',
        'id': nuevo_usuario.ID_Usuario
        }), 200

    except Exception as e:
        db.session.rollback()
        print("⚠️ Error en registrar_usuario_acudiente:", e)
        return jsonify({'message': f'Error interno del servidor: {str(e)}'}), 500


# 🔹 Registrar relación acudiente ↔ estudiante
@Administrador_bp.route('/registrar_detalle_acudiente', methods=['POST'])
def registrar_detalle_acudiente():
    try:
        data = request.get_json(force=True)
        print("📦 Datos recibidos en detalle acudiente:", data)

        # Validación básica
        if not data.get('ID_Usuario') or not data.get('ID_Estudiante'):
            return jsonify({'message': '❌ Faltan datos obligatorios (acudiente o estudiante).'}), 400

        nuevo_acudiente = Acudiente(
            ID_Usuario=data['ID_Usuario'],
            ID_Estudiante=data['ID_Estudiante'],
            Parentesco=data['Parentesco'],
            Estado=data['Estado']
        )

        db.session.add(nuevo_acudiente)
        db.session.commit()

        return jsonify({'message': '✅ Relación acudiente-estudiante registrada correctamente.'}), 200

    except Exception as e:
        db.session.rollback()
        print("⚠️ Error en registrar_detalle_acudiente:", e)
        return jsonify({'message': f'Error interno del servidor: {str(e)}'}), 500


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


@Administrador_bp.route('/manual')
def manual():
    return render_template('Administrador/ManualUsuario.html')


@Administrador_bp.route('/resumensemanal')
def resumensemanal():
    return render_template('Administrador/ResumenSemanal.html')

@Administrador_bp.route('/resumensemanal/registro', methods=['POST'])
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


@Administrador_bp.route('/registrotutorias')
def registrotutorias():
    return render_template('Administrador/RegistroTutorías.html')

@Administrador_bp.route("/tutorias/historial", methods=["GET"])
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
    
@Administrador_bp.route("/tutorias/registro", methods=["POST"])
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
    
    
@Administrador_bp.route('/comunicacion')
def comunicacion():
    return render_template('Administrador/Comunicación.html')


@Administrador_bp.route("/reuniones", methods=["GET"])
def reunion():
    return render_template("Administrador/Reunion.html")

# ---- Guardar reunión ----


@Administrador_bp.route("/reuniones", methods=["POST"])
def guardar_reunion():
    data = request.get_json()
    try:
        nueva_reunion = Reuniones(
            FechaReunion=datetime.strptime(data["fecha"], "%Y-%m-%d"),
            TemaATratar=data["tema"],
            NombreOrganizador=data["organizador"],
            CargoOrganizador=data["cargo"],
            NombresInvitados=data["invitados"],
            LinkReunion=data["link"]
        )
        db.session.add(nueva_reunion)
        db.session.commit()
        
        # 🚨 CAMBIO AQUÍ: Devolver los datos formateados
        return jsonify({
            "success": True,
            "reunion": {
                "fecha": nueva_reunion.FechaReunion.strftime("%Y-%m-%d"),
                "tema": nueva_reunion.TemaATratar,
                "organizador": nueva_reunion.NombreOrganizador,
                "cargo": nueva_reunion.CargoOrganizador,
                "invitados": nueva_reunion.NombresInvitados,
                "link": nueva_reunion.LinkReunion
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)})

# ---- Historial ----
@Administrador_bp.route("/reuniones/historial", methods=["GET"])
def historial_reuniones():
    # 🚨 CAMBIO CLAVE: Añadir .limit(3) a la consulta
    reuniones = Reuniones.query.order_by(Reuniones.FechaReunion.desc()).limit(3).all()
    result = [
        {
            "fecha": r.FechaReunion.strftime("%Y-%m-%d"),
            "tema": r.TemaATratar,
            "organizador": r.NombreOrganizador,
            "cargo": r.CargoOrganizador,
            "invitados": r.NombresInvitados,
            "link": r.LinkReunion
        }
        for r in reuniones
    ]
    return jsonify(result)


UPLOAD_FOLDER = os.path.join('static', 'uploads', 'noticias')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@Administrador_bp.route('/noticias')
def noticias():
    return render_template('Administrador/Noticias.html')

# En administradores.py

@Administrador_bp.route("/noticias/registro", methods=["POST"])
@login_required 
def registrar_noticia():
    try:
        titulo = request.form.get("titulo")
        # ✅ CORRECCIÓN: Usar 'contenido'
        contenido = request.form.get("contenido") 
        fecha_str = request.form.get("fecha")
        creado_por_rol = request.form.get("creadoPor")
        archivo = request.files.get("archivo")

        if not titulo or not contenido:
            return jsonify({"success": False, "error": "El título y la redacción son obligatorios."}), 400

        # Conversión de fecha
        # Asegúrate de que el formato de fecha coincida con el envío del formulario (YYYY-MM-DD)
        try:
            fecha_noticia = datetime.strptime(fecha_str, '%Y-%m-%d')
        except (ValueError, TypeError):
            fecha_noticia = datetime.utcnow() # Usa la fecha actual si falla la conversión

        # Guardar imagen si existe
        ruta_para_bd = None
        if archivo and archivo.filename != '':
            nombre_archivo_seguro = secure_filename(archivo.filename)
            # Define la carpeta de destino absoluta. Asumo 'static/uploads' existe.
            carpeta_destino = os.path.join(current_app.root_path, 'static', 'uploads')
            
            # Asegúrate de que la carpeta exista
            os.makedirs(carpeta_destino, exist_ok=True)
            
            ruta_guardado = os.path.join(carpeta_destino, nombre_archivo_seguro)
            archivo.save(ruta_guardado)
            
            # Guardamos una ruta RELATIVA en la BD, luego se construye la URL pública con url_for
            # Evita duplicar /static cuando se serializa en el historial
            ruta_para_bd = f'uploads/{nombre_archivo_seguro}'

        # El campo CreadoPor en tu modelo Noticias debe ser un campo de texto (string)
        # o un ID de usuario. Lo mantendré como ID, y añadiremos el rol.
        
        # Opcional: Si quieres guardar el rol junto con el ID del usuario
        # Asumiendo que Noticias.CreadoPor solo guarda el ID_Usuario (FK)
        # y que el Rol se podría obtener de la sesión si es necesario
        
        nueva_noticia = Noticias(
            Fecha=fecha_noticia, 
            Titulo=titulo,
            Redaccion=contenido, # ✅ Correcto: usa 'contenido'
            Archivo=ruta_para_bd, 
            CreadoPor=current_user.ID_Usuario, # Asumiendo que es el ID del usuario
            # Podrías agregar un campo "RolPublicador" si lo necesitas en la DB
            # RolPublicador=creado_por_rol 
        )

        db.session.add(nueva_noticia)
        db.session.commit()

        return jsonify({"success": True, "message": "✅ Noticia registrada correctamente."})

    except Exception as e:
        db.session.rollback()
        print(f"⚠️ Error al registrar noticia: {e}")
        return jsonify({"success": False, "error": f"Error de servidor: {e}"}), 500
    
@Administrador_bp.route("/noticias/historial", methods=["GET"])
def historial_noticias():
    """
    Ruta API para devolver las 4 noticias más recientes.
    """
    try:
        # ✅ Traer solo las 4 noticias más recientes por creación (ID descendente)
        # Usar ID evita que una fecha ingresada manualmente más antigua oculte la noticia recién creada
        noticias = Noticias.query.order_by(Noticias.ID_Noticia.desc()).limit(4).all()

        result = []
        for n in noticias:
            # Construir URL de archivo evitando duplicaciones:
            # - Si en BD está guardado como 'uploads/archivo.jpg' => usar url_for('static', filename=...)
            # - Si en BD ya está como '/static/...' => usar tal cual
            if n.Archivo:
                if isinstance(n.Archivo, str) and n.Archivo.strip().startswith('/static/'):
                    archivo_url = n.Archivo
                else:
                    archivo_url = url_for('static', filename=n.Archivo)
            else:
                archivo_url = None

            autor = "Sistema"
            try:
                if getattr(n, "creador", None):
                    nombre = getattr(n.creador, "Nombre", None) or ""
                    apellido = getattr(n.creador, "Apellido", None) or ""
                    nombre_completo = f"{nombre} {apellido}".strip()
                    if nombre_completo:
                        autor = nombre_completo
            except Exception:
                pass

            result.append({
                "id": n.ID_Noticia,
                "titulo": n.Titulo,
                "redaccion": n.Redaccion,
                "archivo_url": archivo_url,
                "fecha": n.Fecha.strftime("%Y-%m-%d"),
                "creado_por": autor
            })

        return jsonify({"success": True, "noticias": result})
    
    except Exception as e:
        print(f"Error al cargar historial de noticias: {e}")
        return jsonify({"success": False, "error": "Error de servidor al cargar noticias"}), 500



@Administrador_bp.route('/circulares')
def circulares():
    try:
        carpeta = os.path.join(current_app.root_path, 'static', 'uploads', 'circulares')
        os.makedirs(carpeta, exist_ok=True)
        files = []
        for f in os.listdir(carpeta):
            full = os.path.join(carpeta, f)
            if os.path.isfile(full):
                files.append((f, os.path.getmtime(full)))
        files = [f for f, _ in sorted(files, key=lambda x: x[1], reverse=True)]
        return render_template('Administrador/Circulares.html', files=files)
    except Exception:
        return render_template('Administrador/Circulares.html', files=[])

@Administrador_bp.route('/circulares/registro', methods=['POST'])
@login_required
def registrar_circular():
    try:
        archivo = request.files.get('file')
        if not archivo or archivo.filename == '':
            return jsonify({"success": False, "error": "No se envió archivo."}), 400

        nombre_archivo = secure_filename(archivo.filename)
        carpeta = os.path.join(current_app.root_path, 'static', 'uploads', 'circulares')
        os.makedirs(carpeta, exist_ok=True)
        ruta = os.path.join(carpeta, nombre_archivo)
        archivo.save(ruta)

        url_publica = url_for('static', filename=f'uploads/circulares/{nombre_archivo}')
        return jsonify({"success": True, "file": nombre_archivo, "url": url_publica})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@Administrador_bp.route('/circulares/historial', methods=['GET'])
def historial_circulares():
    try:
        carpeta = os.path.join(current_app.root_path, 'static', 'uploads', 'circulares')
        os.makedirs(carpeta, exist_ok=True)
        items = []
        for f in os.listdir(carpeta):
            full = os.path.join(carpeta, f)
            if os.path.isfile(full):
                items.append({
                    "nombre": f,
                    "url": url_for('static', filename=f'uploads/circulares/{f}'),
                    "mtime": os.path.getmtime(full)
                })
        items.sort(key=lambda x: x["mtime"], reverse=True)
        top = items[:5]
        return jsonify({"success": True, "circulares": top})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@Administrador_bp.route('/noticias_vistas')
def noticias_vistas():
    return render_template('Administrador/NoticiasVistas.html')


@Administrador_bp.route('/usuarios')
def usuarios():
    return render_template('Administrador/Usuarios.html')



# CREAR ASIGNATURAS #

@Administrador_bp.route('/asignaturas', methods=['GET'])
def asignaturas():
    # Listado de docentes y cursos activos
    docentes = Usuario.query.filter_by(Rol='Docente', Estado='Activo').all()
    cursos = Curso.query.filter_by(Estado='Activo').all()

    # Consultar asignaturas con el docente asignado
    asignaturas = db.session.query(
        Asignatura.ID_Asignatura,
        Asignatura.Nombre,
        Asignatura.Descripcion,
        Asignatura.Grado,
        Asignatura.Area,
        Asignatura.Estado,
        Usuario.Nombre.label('DocenteNombre'),
        Usuario.Apellido.label('DocenteApellido'),
        Usuario.ID_Usuario.label('DocenteID')
    ).join(Docente_Asignatura, Docente_Asignatura.ID_Asignatura == Asignatura.ID_Asignatura)\
     .join(Usuario, Usuario.ID_Usuario == Docente_Asignatura.ID_Docente)\
     .all()

    docentes_asignados = {docente.ID_Usuario: [] for docente in docentes}
    for asig in asignaturas:
        docentes_asignados[asig.DocenteID].append(asig.Nombre)


    return render_template(
        'Administrador/Asignaturas.html',
        asignaturas=asignaturas,
        docentes=docentes,
        cursos=cursos,
        docentes_asignados=docentes_asignados 
    )



# GUARDAR NUEVA ASIGNATURA

@Administrador_bp.route('/asignaturas/guardar', methods=['POST'])
def guardar_asignatura():
    nombre = request.form.get('nombre')
    descripcion = request.form.get('descripcion')
    ciclo = request.form.get('ciclo')
    id_docente = request.form.get('id_docente')

    if not all([nombre, id_docente]):
        return jsonify({"error": "Faltan datos obligatorios"}), 400

    try:
        id_docente = int(id_docente)
        docente = Usuario.query.get(id_docente)
        if not docente:
            return jsonify({"error": "Docente no encontrado"}), 404

        codigo = f"C-{nombre[:3].upper()}-{ciclo}"

        existente = Asignatura.query.filter_by(CodigoAsignatura=codigo).first()
        if existente:
            return jsonify({"error": f"Ya existe una asignatura con el código {codigo}"}), 400

        asignatura = Asignatura(
            Nombre=nombre,
            Descripcion=descripcion,
            Grado=ciclo,
            Area="General",
            CodigoAsignatura=codigo,
            Estado="Activa"
        )

        relacion = Docente_Asignatura(docente=docente, asignatura=asignatura)
        db.session.add(asignatura)
        db.session.add(relacion)
        db.session.commit()

        return jsonify({"success": "Asignatura registrada correctamente"})

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500



# EDITAR ASIGNATURA

@Administrador_bp.route('/asignaturas/editar/<int:id>', methods=['POST'])
def editar_asignatura(id):
    try:
        asignatura = Asignatura.query.get(id)
        if not asignatura:
            return jsonify({"error": "Asignatura no encontrada"}), 404

        asignatura.Nombre = request.form.get('nombre')
        asignatura.Descripcion = request.form.get('descripcion')
        asignatura.Grado = request.form.get('ciclo')
        db.session.commit()

        return jsonify({"success": "Asignatura actualizada correctamente"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# DESACTIVAR / ACTIVAR ASIGNATURA

@Administrador_bp.route('/asignaturas/desactivar/<int:id>', methods=['POST'])
def desactivar_asignatura(id):
    try:
        asignatura = Asignatura.query.get(id)
        if not asignatura:
            return jsonify({"error": "Asignatura no encontrada"}), 404

        asignatura.Estado = "Inactiva"
        db.session.commit()
        return jsonify({"success": "Asignatura desactivada correctamente"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    
    
@Administrador_bp.route('/asignaturas/reactivar/<int:id>', methods=['POST'])
@login_required
def reactivar_asignatura(id):
    asignatura = Asignatura.query.get_or_404(id)
    try:
        asignatura.Estado = "Activa"  # Debe coincidir exactamente con el Enum
        db.session.commit()
        return jsonify({'success': 'Asignatura reactivada correctamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)})



# 📌 Endpoint para obtener todas las asignaturas (API JSON)
@Administrador_bp.route('/api/asignaturas', methods=['GET'])
def api_get_asignaturas():
    asignaturas = Asignatura.query.all()
    data = []
    for a in asignaturas:
        data.append({
            "id": a.ID_Asignatura,
            "nombre": a.Nombre,
            "descripcion": a.Descripcion,
            "grado": a.Grado,
            "area": a.Area,
            "codigo": a.CodigoAsignatura,
            "estado": a.Estado
        })
    return jsonify(data)


# 📌 Endpoint para agregar una nueva asignatura
@Administrador_bp.route('/api/asignaturas', methods=['POST'])
def crear_asignatura():
    data = request.get_json()

    nombre = data.get('nombre')
    descripcion = data.get('descripcion')
    grado = data.get('grado')
    area = data.get('area', '')
    codigo = data.get('codigo')
    id_docente = data.get('id_docente')

    # Crear la asignatura
    nueva = Asignatura(
        Nombre=nombre,
        Descripcion=descripcion,
        Grado=grado,
        Area=area,
        CodigoAsignatura=codigo,
        Estado='Activa'
    )
    db.session.add(nueva)
    db.session.flush()  # Para obtener ID antes del commit

    # Crear relación docente-asignatura
    if id_docente:
        relacion = Docente_Asignatura(
            ID_Docente=id_docente,
            ID_Asignatura=nueva.ID_Asignatura
        )
        db.session.add(relacion)

    db.session.commit()

    return jsonify({"success": True, "id": nueva.ID_Asignatura})


@Administrador_bp.route('/api/docentes', methods=['GET'])
def obtener_docentes():
    docentes = Usuario.query.filter_by(Rol='Docente', Estado='Activo').all()
    data = [
        {
            "id": d.ID_Usuario,
            "nombre": f"{d.Nombre} {d.Apellido}"
        }
        for d in docentes
    ]
    return jsonify(data)


@Administrador_bp.route('/api/asignaturas', methods=['GET'])
def listar_asignaturas():
    asignaturas = Asignatura.query.all()
    data = []
    for a in asignaturas:
        relacion = Docente_Asignatura.query.filter_by(ID_Asignatura=a.ID_Asignatura).first()
        docente_nombre = None
        if relacion and relacion.docente:
            docente_nombre = f"{relacion.docente.Nombre} {relacion.docente.Apellido}"
        data.append({
            "id": a.ID_Asignatura,
            "nombre": a.Nombre,
            "descripcion": a.Descripcion,
            "grado": a.Grado,
            "area": a.Area,
            "codigo": a.CodigoAsignatura,
            "estado": a.Estado,
            "profesor": docente_nombre
        })
    return jsonify(data)

#----------------------------------------------------------------------
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


@Administrador_bp.route('/notas_registro')
def notas_registro():
    return render_template('Administrador/Notas_Registro.html')

@Administrador_bp.route('/notas_consultar')
def notas_consultar():
    cursos = Curso.query.filter_by(Estado='Activo').order_by(Curso.Grado, Curso.Grupo).all()
    return render_template('Administrador/Notas_Consultar.html', cursos=cursos)


# GESTIÓN DE LA OBSERVACIÓN #

@Administrador_bp.route('/observador')
def observador():

    observaciones = (
        db.session.query(Observacion, Usuario, Curso)
        .join(Matricula, Observacion.ID_Matricula == Matricula.ID_Matricula)
        .join(Usuario, Matricula.ID_Estudiante == Usuario.ID_Usuario)
        .join(Curso, Matricula.ID_Curso == Curso.ID_Curso)
        .all()
    )

    # Listar solo los estudiantes
    estudiantes = Usuario.query.filter_by(Rol='Estudiante').all()

    # Listar cursos disponibles
    cursos = Curso.query.all()

    return render_template(
        'Administrador/Observador.html',
        observaciones=observaciones,
        estudiantes=estudiantes,
        cursos=cursos
    )


@Administrador_bp.route('/observador/registrar', methods=['POST'])
def registrar_observacion():
    data = request.form

    id_estudiante = data.get('id_estudiante')
    id_curso = data.get('id_curso')

    if not id_estudiante or not id_curso:
        return jsonify({"status": "error", "message": "Debe seleccionar estudiante y curso"}), 400

    # Buscar la matrícula del estudiante en el curso seleccionado
    matricula = Matricula.query.filter_by(ID_Estudiante=id_estudiante, ID_Curso=id_curso).first()
    if not matricula:
        return jsonify({"status": "error", "message": "El estudiante no está matriculado en este curso"}), 400

    try:
        nueva_obs = Observacion(
            Fecha=datetime.strptime(data.get('fecha'), "%Y-%m-%d").date(),
            Descripcion=data.get('descripcion'),
            Tipo=data.get('tipo'),
            NivelImportancia=data.get('nivelImportancia'),
            Recomendacion=data.get('recomendacion'),
            Estado="Activa",
            ID_Matricula=matricula.ID_Matricula
        )

        db.session.add(nueva_obs)
        db.session.commit()
        return jsonify({"status": "ok", "message": "✅ Observación registrada correctamente"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": f"Error al guardar: {str(e)}"}), 500


@Administrador_bp.route('/calculo_promedio')
def calculo_promedio():
    return render_template('Administrador/CalculoPromedio.html')

@Administrador_bp.route('/promedios', methods=['GET'])
def promedios_por_curso():
    try:
        curso_id_raw = request.args.get('curso_id')  # puede ser 'all' o un int
        periodo = request.args.get('periodo', type=int)

        if not periodo:
            return jsonify({"success": False, "error": "Falta parámetro periodo"}), 400

        cursos_q = Curso.query.filter_by(Estado='Activo')
        if curso_id_raw and curso_id_raw != 'all':
            try:
                curso_id = int(curso_id_raw)
                cursos_q = cursos_q.filter(Curso.ID_Curso == curso_id)
            except ValueError:
                return jsonify({"success": False, "error": "curso_id inválido"}), 400

        cursos = cursos_q.all()
        cursos_ids = [c.ID_Curso for c in cursos]

        if not cursos_ids:
            return jsonify({"success": True, "items": []})

        # Estudiantes matriculados en los cursos seleccionados
        est_q = (
            db.session.query(Usuario.ID_Usuario.label('id'), Usuario.Nombre, Usuario.Apellido, Usuario.NumeroDocumento,
                             Curso.ID_Curso.label('curso_id'), Curso.Grado, Curso.Grupo)
            .join(Matricula, Matricula.ID_Estudiante == Usuario.ID_Usuario)
            .join(Curso, Curso.ID_Curso == Matricula.ID_Curso)
            .filter(Usuario.Rol == 'Estudiante', Matricula.ID_Curso.in_(cursos_ids))
        )
        estudiantes = est_q.all()

        if not estudiantes:
            return jsonify({"success": True, "items": []})

        est_ids = [e.id for e in estudiantes]

        # Notas por estudiante para el período indicado
        notas = (
            db.session.query(
                Nota_Calificaciones.ID_Estudiante.label('id_est'),
                func.avg(Nota_Calificaciones.Promedio_Final).label('promedio')
            )
            .filter(Nota_Calificaciones.ID_Estudiante.in_(est_ids), Nota_Calificaciones.Periodo == periodo)
            .group_by(Nota_Calificaciones.ID_Estudiante)
            .all()
        )
        map_prom = {n.id_est: float(n.promedio) if n.promedio is not None else 0.0 for n in notas}

        items = []
        for e in estudiantes:
            prom = map_prom.get(e.id, 0.0)
            items.append({
                "estudiante_id": e.id,
                "nombre": f"{e.Apellido} {e.Nombre}",
                "documento": e.NumeroDocumento,
                "curso": f"{e.Grado}{e.Grupo}",
                "curso_id": e.curso_id,
                "promedio": round(prom, 2)
            })

        # Ordenar por curso y nombre
        items.sort(key=lambda x: (x['curso'], x['nombre']))
        return jsonify({"success": True, "items": items})
    except Exception as e:
        print('Error en /promedios:', e)
        return jsonify({"success": False, "error": str(e)}), 500

# ------------------- ENCUESTAS -------------------


@Administrador_bp.route('/encuestas')
def encuesta():
    encuestas = Encuesta.query.all()
    return render_template('Administrador/Encuestas.html', encuestas=encuestas)

# Crear encuesta
@Administrador_bp.route('/encuestas/crear', methods=['GET', 'POST'])
def crear_encuesta():
    if request.method == 'POST':
        # Datos principales
        titulo = request.form.get('Titulo')
        descripcion = request.form.get('Descripcion')
        fecha_cierre = request.form.get('FechaCierre')
        dirigido_a = request.form.get('DirigidoA')
        creado_por = session.get('user_id')

        # Archivo opcional
        archivo = request.files.get("Archivo")
        archivo_nombre = None
        if archivo and archivo.filename != '':
            archivo_nombre = secure_filename(archivo.filename)
            archivo.save(os.path.join(current_app.config['UPLOAD_FOLDER'], archivo_nombre))

        # Crear encuesta
        nueva_encuesta = Encuesta(
            Titulo=titulo,
            Descripcion=descripcion,
            FechaCierre=datetime.strptime(fecha_cierre, "%Y-%m-%d") if fecha_cierre else None,
            DirigidoA=dirigido_a,
            CreadoPor=creado_por
        )
        db.session.add(nueva_encuesta)
        db.session.flush()  # Para obtener ID_Encuesta antes de commit

        # Guardar preguntas dinámicas
        textos = request.form.getlist('TextoPregunta[]')
        tipos = request.form.getlist('TipoRespuesta[]')

        for texto, tipo in zip(textos, tipos):
            if texto.strip():  # Evitar preguntas vacías
                pregunta = Encuesta_Pregunta(
                    ID_Encuesta=nueva_encuesta.ID_Encuesta,
                    TextoPregunta=texto,
                    TipoRespuesta=tipo
                )
                db.session.add(pregunta)

        db.session.commit()
        flash('✅ Encuesta creada correctamente', 'success')
        return redirect(url_for('Administrador.encuesta'))

    return render_template('Administrador/CrearEncuesta.html')



@Administrador_bp.route('/encuestas/<int:id_encuesta>/editar', methods=['GET','POST'])
def editar_encuesta(id_encuesta):
    encuesta = Encuesta.query.get_or_404(id_encuesta)
    if request.method == 'POST':
        encuesta.Titulo = request.form.get('titulo')
        encuesta.Descripcion = request.form.get('descripcion')
        fecha_cierre = request.form.get('fecha_cierre')
        encuesta.FechaCierre = datetime.strptime(fecha_cierre, "%Y-%m-%d") if fecha_cierre else None
        encuesta.DirigidoA = request.form.get('dirigido_a')

        # Actualizar preguntas existentes o agregar nuevas
        preguntas_texto = request.form.getlist('pregunta[]')
        tipos_respuesta = request.form.getlist('tipo_respuesta[]')
        
        # Limpiar preguntas antiguas
        encuesta.preguntas.clear()
        for texto, tipo in zip(preguntas_texto, tipos_respuesta):
            if texto.strip():
                db.session.add(Encuesta_Pregunta(
                    ID_Encuesta=encuesta.ID_Encuesta,
                    TextoPregunta=texto,
                    TipoRespuesta=tipo
                ))

        db.session.commit()
        flash('✅ Encuesta actualizada', 'success')
        return redirect(url_for('Administrador.encuesta'))

    return render_template('Administrador/EditarEliminarEncuesta.html', encuesta=encuesta)




# Desactivar / Activar encuesta
@Administrador_bp.route('/encuestas/<int:id_encuesta>/toggle', methods=['POST'])
def toggle_encuesta(id_encuesta):
    encuesta = Encuesta.query.get_or_404(id_encuesta)
    encuesta.Activa = not encuesta.Activa
    db.session.commit()
    estado = 'activada' if encuesta.Activa else 'desactivada'
    flash(f'✅ Encuesta {estado}', 'success')
    return redirect(url_for('Administrador.encuesta'))

# Ver respuestas de la encuesta
@Administrador_bp.route('/encuestas/<int:id_encuesta>/respuestas')
def ver_respuestas_encuesta(id_encuesta):
    encuesta = Encuesta.query.get_or_404(id_encuesta)
    respuestas = Encuesta_Respuesta.query.filter_by(ID_Encuesta=id_encuesta).all()
    return render_template('Administrador/ResultadosEncuesta.html', encuesta=encuesta, respuestas=respuestas)

# API para listar todas las encuestas con sus preguntas
@Administrador_bp.route('/api/encuestas', methods=['GET'])
def api_encuestas():
    encuestas = Encuesta.query.all()
    data = []

    for e in encuestas:
        preguntas = []
        for p in e.preguntas:  # Usa la relación definida en tu modelo
            preguntas.append({
                "id": p.ID_Pregunta,
                "texto": p.TextoPregunta,
                "tipo": p.TipoRespuesta
            })

        data.append({
            "id": e.ID_Encuesta,
            "titulo": e.Titulo,
            "descripcion": e.Descripcion,
            "activa": e.Activa,
            "preguntas": preguntas
        })

    return jsonify(data)


@Administrador_bp.route('/ver_promedio')
def ver_promedio():
    return render_template('Administrador/VerPromedio.html')


# CONFIGURACIÓN ACADÉMICA


@Administrador_bp.route('/configuracion_academica')
def configuracion_academica():
    return render_template('Administrador/ConfiguracionAcademica.html')

@Administrador_bp.route('/get_periodos')
def get_periodos():
    periodos = Periodo.query.order_by(Periodo.NumeroPeriodo).all()
    data = {}
    for p in periodos:
        data[p.NumeroPeriodo] = {
            'inicio': p.FechaInicial.strftime('%Y-%m-%d') if p.FechaInicial else '',
            'fin': p.FechaFinal.strftime('%Y-%m-%d') if p.FechaFinal else ''
        }
    return jsonify(data)

@Administrador_bp.route('/guardar_periodos', methods=['POST'])
def guardar_periodos():
    try:
        data = request.get_json(force=True)
        for i in range(1, 5):
            inicio = data.get(f'periodo{i}_inicio')
            fin = data.get(f'periodo{i}_fin')
            
            if not inicio or not fin:
                continue
            
            periodo = Periodo.query.filter_by(NumeroPeriodo=i).first()
            if not periodo:
                periodo = Periodo(NumeroPeriodo=i, Anio=str(datetime.now().year))
                db.session.add(periodo)
            
            periodo.FechaInicial = datetime.strptime(inicio, '%Y-%m-%d').date()
            periodo.FechaFinal = datetime.strptime(fin, '%Y-%m-%d').date()
        
        db.session.commit()
        return jsonify({'message': '✅ Periodos guardados correctamente.'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'❌ Error al guardar los periodos: {str(e)}'}), 500

@Administrador_bp.route('/configuracion_academica2')
def configuracion_academica2():
    return render_template('Administrador/ConfiguracionAcademica2.html')

@Administrador_bp.route('/configuracion_academica3')
def configuracion_academica3():
    return render_template('Administrador/ConfiguracionAcademica3.html')


@Administrador_bp.route('/repitentes')
def repitentes():
    repitentes = Estudiantes_Repitentes.query.all()
    return render_template('Administrador/repitentes.html', repitentes=repitentes)


@Administrador_bp.route('/repitentes/agregar', methods=['POST'])
def agregar_repitente():
    try:
        tipo = request.form.get('tipo_documento')
        doc = request.form.get('numero_documento')
        nombre = request.form.get('nombre')
        curso = request.form.get('curso')

        # Buscar matrícula actual del estudiante
        matricula = Matricula.query.filter_by(NumeroDocumento=doc).first()
        id_matricula = matricula.ID_Matricula if matricula else None
        esta_matriculado = matricula is not None 

        # Buscar si ya existe en la tabla de repitentes
        existente = Estudiantes_Repitentes.query.filter_by(NumeroDocumento=doc).first()

        if existente:
            existente.Veces += 1
            existente.FechaRegistro = datetime.utcnow()  # 🔹 Actualiza la fecha
            if not existente.ID_Matricula and id_matricula:
                existente.ID_Matricula = id_matricula
            db.session.commit()
            return jsonify({'success': True, 'message': 'Veces y fecha actualizadas correctamente'})
        else:
            # Crear nuevo registro
            nuevo = Estudiantes_Repitentes(
                TipoDocumento=tipo,
                NumeroDocumento=doc,
                NombreCompleto=nombre,
                Curso=curso,
                FechaRegistro=datetime.utcnow(),
                Veces=1,
                ID_Matricula=id_matricula,
                Matriculado=esta_matriculado
            )
            db.session.add(nuevo)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Estudiante repitente registrado correctamente'})

    except Exception as e:
        print("❌ Error:", e)
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500



@Administrador_bp.route('/cursos')
def cursos():
    cursos = Curso.query.all()
    return render_template('Administrador/Cursos.html', cursos=cursos)


# ---------------------- Historial Académico ----------------------

@Administrador_bp.route('/historialacademico')
def historialacademico():
    # Esta ruta ya no requiere el parámetro en la URL
    return render_template('Administrador/HistorialAcademico.html')
    
    
@Administrador_bp.route('/api/historialacademico/buscar_documento/<numero_documento>', methods=['GET'])
@login_required 
def api_buscar_estudiante_por_documento(numero_documento):
    
    doc_limpio = numero_documento.strip()
    
    # 1. Buscar la Matrícula más reciente por NumeroDocumento (Usando TRIM())
    matricula = Matricula.query.filter(
        func.trim(Matricula.NumeroDocumento) == doc_limpio
    ).order_by(Matricula.AnioLectivo.desc()).first()
    
    if not matricula:
        return jsonify({"error": "Estudiante no encontrado o sin matrícula activa."}), 404

    # 2. Obtener el registro del Estudiante (Usuario)
    estudiante = Usuario.query.get(matricula.ID_Estudiante)
    
    if not estudiante:
         return jsonify({"error": "Error interno: Matrícula encontrada, pero sin registro de Usuario asociado."}), 500
        
    # 3. Construir el Nombre del Curso correctamente
    if hasattr(matricula, 'curso') and matricula.curso:
        # CONCATENAMOS GRADO y GRUPO para formar el nombre visible
        curso_nombre = f"{matricula.curso.Grado} {matricula.curso.Grupo}"
        grado = matricula.curso.Grado
    else:
        curso_nombre = "N/A"
        grado = "N/A"

    return jsonify({
        "ID_Usuario": estudiante.ID_Usuario,
        "NombreCompleto": f"{estudiante.Nombre} {estudiante.Apellido}", 
        "NumeroDocumento": estudiante.NumeroDocumento, 
        "ID_Matricula_Reciente": matricula.ID_Matricula,
        "Grado": grado,
        "Curso": curso_nombre
    })
    
@Administrador_bp.route('/api/historialacademico/datos_estudiante/<int:matricula_id>', methods=['GET'])
@login_required 
def api_obtener_datos_estudiante(matricula_id):
    # 1. Buscar la Matrícula
    matricula = Matricula.query.get(matricula_id)
    
    if not matricula:
        return jsonify({"error": "Matrícula no encontrada."}), 404
        
    # 2. Buscar el Estudiante (Usuario)
    estudiante = Usuario.query.get(matricula.ID_Estudiante)
    
    if not estudiante:
        return jsonify({"error": "Estudiante no asociado a esta matrícula."}), 404
    
    # 3. Construir el nombre del curso y obtener el grado
    curso_nombre = "N/A"
    grado = "N/A"
    if hasattr(matricula, 'curso') and matricula.curso:
        curso_nombre = f"{matricula.curso.Grado} {matricula.curso.Grupo}"
        grado = matricula.curso.Grado

    # 4. Devolver el JSON con los datos
    return jsonify({
        "NombreCompleto": f"{estudiante.Nombre} {estudiante.Apellido}",
        "NumeroDocumento": estudiante.NumeroDocumento,
        "Grado": grado,
        "Curso": curso_nombre,
    })

@Administrador_bp.route('/historialacademico2') 
def historialacademico2():
    return render_template('Administrador/HistorialAcademico2.html')
    
@Administrador_bp.route('/api/historialacademico/historiales/<int:matricula_id>', methods=['GET'])
@login_required 
def api_listar_historiales_por_matricula(matricula_id):
    # Obtener todos los registros de Historial Académico para esa matrícula
    # Asegúrate de que el modelo Historial_Academico se ha importado correctamente
    historiales = Historial_Academico.query.filter_by(ID_Matricula=matricula_id).order_by(Historial_Academico.Anio.desc(), Historial_Academico.Periodo.desc()).all()
    
    # Si no hay historiales, devuelve una lista vacía, lo cual el JS maneja
    if not historiales:
        return jsonify([]), 200 
        
    historiales_data = []
    for h in historiales:
        historiales_data.append({
            "ID_Historial": h.ID_Historial,
            "Anio": h.Anio,
            "Periodo": h.Periodo,
            "Descripcion": h.Descripcion,
            # Asegúrate que CreadoEn no sea NULL o maneja el error de strftime
            "CreadoEn": h.CreadoEn.strftime('%Y-%m-%d') if h.CreadoEn else None 
        })
        
    return jsonify(historiales_data)


@Administrador_bp.route('/api/historialacademico/notas/<int:id_historial>', methods=['GET'])
@login_required 
def api_historial_academico_notas(id_historial):
    
    # --- 1. Verificación de Autenticación (API Guard) ---
    if not current_user.is_authenticated:
        return jsonify({"error": "No autorizado. Inicie sesión nuevamente."}), 401

    try:
        # --- 2. Búsqueda del Historial y Datos del Estudiante/Curso ---
        historial = Historial_Academico.query.get(id_historial)
        
        if not historial:
            return jsonify({"error": f"Historial con ID {id_historial} no encontrado."}), 404
            
        # Obtener los datos relacionados (Matrícula -> Estudiante/Curso)
        matricula = Matricula.query.get(historial.ID_Matricula)
        if not matricula:
            return jsonify({"error": "Matrícula no encontrada para este historial."}), 404
            
        # Utilizamos el modelo 'Usuario' y 'Curso' (en singular)
        estudiante = Usuario.query.get(matricula.ID_Estudiante)
        curso = Curso.query.get(matricula.ID_Curso)
        
        # --- 3. Búsqueda de Notas (Solo Nota_Calificaciones) ---
        
        # Realiza un JOIN entre Nota_Calificaciones y Asignatura para obtener el nombre.
        # CRUCIAL: Se corrigió la referencia a Notas_Calificaciones a Nota_Calificaciones.
        notas_query = db.session.query(Nota_Calificaciones, Asignatura)\
                            .join(Asignatura)\
                            .filter(Nota_Calificaciones.ID_Historial == id_historial)\
                            .all()
        
        notas_data = []
        for nota_obj, asignatura_obj in notas_query:
            notas_data.append({
                "ID_Nota": nota_obj.ID_Nota,
                "Materia": asignatura_obj.Nombre, 
                "N1": f"{nota_obj.N1:.1f}" if nota_obj.N1 is not None else "N/A", # Formato con un decimal
                "N2": f"{nota_obj.N2:.1f}" if nota_obj.N2 is not None else "N/A",
                "N3": f"{nota_obj.N3:.1f}" if nota_obj.N3 is not None else "N/A",
                "N4": f"{nota_obj.N4:.1f}" if nota_obj.N4 is not None else "N/A",
                # Asumo que estos campos están en tu tabla Nota_Calificaciones
                "PromedioCortes": f"{nota_obj.PromedioCortes:.1f}" if nota_obj.PromedioCortes is not None else "N/A",
                "NotaFinal": f"{nota_obj.NotaFinal:.1f}" if nota_obj.NotaFinal is not None else "N/A",
            })

        # --- 4. Búsqueda de Recuperaciones (ELIMINADO y reemplazado con lista vacía) ---
        # Como no tienes la tabla, simplemente devolvemos una lista vacía para que el frontend funcione.
        recup_data = []
            
        # --- 5. Construcción de la Respuesta Final ---
        response_data = {
            "EstudianteNombre": f"{estudiante.Nombre} {estudiante.Apellido}" if estudiante else "Estudiante Desconocido",
            "Curso": f"{curso.Grado}-{curso.Nombre}" if curso else "Curso Desconocido",
            "Anio": historial.Anio,
            "Periodo": historial.Periodo,
            "Notas": notas_data,
            "Recuperaciones": recup_data # Se mantiene la clave para evitar romper el frontend
        }
        
        return jsonify(response_data), 200

    except Exception as e:
        # Manejo de cualquier error inesperado
        print(f"Error crítico en api_historial_academico_notas: {e}") 
        return jsonify({"error": "Error interno del servidor al obtener las notas. Verifique la conexión a DB, las importaciones y los nombres de modelos (Usuario, Curso, Nota_Calificaciones)."}), 500
    
    

@Administrador_bp.route('/historialacademico3')
def historialacademico3():
    periodo = request.args.get('periodo')
    return render_template('Administrador/HistorialAcademico3.html', periodo=periodo)



# ----------------- SUB-PÁGINAS -----------------
@Administrador_bp.route('/registrotutorias2')
def registrotutorias2():
    return render_template('Administrador/RegistroTutorías2.html')



@Administrador_bp.route('/gestion_cursos', methods=['GET', 'POST']) 
def gestion_cursos(): # <--- NOMBRE DE LA FUNCIÓN CAMBIADO
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
        try:
            db.session.add(nuevo_curso)
            db.session.commit()
            # OJO: Cambiamos el redirect al nuevo nombre de la ruta
            flash("✅ Curso agregado correctamente", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"❌ Error al agregar curso: {str(e)}", "danger")

        # Redirige a la nueva función
        return redirect(url_for('Administrador.gestion_cursos')) 

    # Para GET (mostrar cursos)
    cursos = Curso.query.all()
    usuarios = Usuario.query.all()
    # Tu template Cursos2.html (la tabla con el formulario) deberá ser llamado aquí.
    return render_template('Administrador/ver_estudiante_curso.html', cursos=cursos, usuarios=usuarios)

@Administrador_bp.route('/cursos/<int:curso_id>/estudiantes') 
def _estudiantes_curso(curso_id):
    try:
        # 1. Decodificar el ID del curso (Ej: 901 -> Grado 9, Grupo 01)
        grado = curso_id // 100
        # zfill(2) asegura que grupos de un dígito (ej: 1) se conviertan en '01'
        grupo = str(curso_id % 100).zfill(2) 
        
        # 2. Buscar el objeto Curso en la DB
        curso_obj = Curso.query.filter_by(Grado=grado, Grupo=grupo).first()

        if not curso_obj:
            flash(f"❌ Curso {curso_id} no encontrado. Asegúrese de que el curso esté registrado.", "danger")
            # Redirige a la ruta principal de gestión de cursos
            return redirect(url_for('Administrador.gestion_cursos'))

        id_curso = curso_obj.ID_Curso

        # 3. Consultar estudiantes matriculados en ese curso
        # ✅ CORRECCIÓN CLAVE: El join usa Matricula.ID_Estudiante como el vínculo al Usuario.
        estudiantes_data = db.session.query(Usuario).join(Matricula).filter(
            Matricula.ID_Curso == id_curso,
            Usuario.Rol == 'Estudiante',
            Usuario.ID_Usuario == Matricula.ID_Estudiante 
        ).all()
        
        # 4. Renderizar la plantilla
        return render_template(
            'Administrador/ver_estudiante_curso.html', 
            curso_id=curso_id, 
            curso_obj=curso_obj, # Enviamos el objeto Curso
            estudiantes=estudiantes_data # Enviamos la lista de estudiantes
        )

    except Exception as e:
        # Esto captura cualquier error de DB o de lógica antes del renderizado
        print(f"Error al obtener estudiantes del curso {curso_id}: {e}")
        db.session.rollback()
        flash(f"❌ Error interno al cargar estudiantes: {str(e)}", "danger")
        return redirect(url_for('Administrador.gestion_cursos'))
    

# Función que procesa el formulario de asistencia
@Administrador_bp.route('/tomar_asistencia/<int:curso_id>', methods=['POST'])
def registrar_asistencia(curso_id): # Dejamos el nombre 'guardar_asistencia'
    try:
        # 1. Obtener y convertir datos
        fecha_asistencia = request.form.get('fecha_asistencia')
        id_programacion = int(request.form.get('id_programacion'))

        # 2. Verificar duplicados
        asistencia_existente = Asistencia.query.filter_by(
            Fecha=fecha_asistencia,
            ID_Programacion=id_programacion
        ).first()

        if asistencia_existente:
            # Para AJAX, devolvemos JSON con error
            return jsonify({
                'status': 'success',
    'message': 'Asistencia registrada correctamente.',
    'curso_id': curso_id,
    'fecha': fecha_asistencia
            }), 409 # Código 409 Conflict

        # 3. Crear registro en Asistencia y hacer commit
        nueva_asistencia = Asistencia(Fecha=fecha_asistencia, ID_Programacion=id_programacion)
        db.session.add(nueva_asistencia)
        db.session.commit()
        id_asistencia = nueva_asistencia.ID_Asistencia

        # 4. Procesar el estado de cada estudiante
        for key, value in request.form.items():
            if key.startswith('asistencia_'):
                id_estudiante = int(key.split('_')[1])
                estado = value
                
                detalle = Detalle_Asistencia(
                    ID_Asistencia=id_asistencia,
                    ID_Estudiante=id_estudiante,
                    Estado_Asistencia=estado
                )
                db.session.add(detalle)
        
        # 5. Commit final de los detalles
        db.session.commit()
        
        # 🟢 ¡RESPUESTA AJAX DE ÉXITO!
        return jsonify({
            'status': 'error',
        'message': "Asistencia para esta sesión ya fue tomada."
            
        })

    except Exception as e:
        # 🛑 Bloque que protege la aplicación de errores de DB 🛑
        db.session.rollback() 
        print(f"\n--- ERROR DE DB AL GUARDAR ASISTENCIA ---\n{e}\n----------------------------------\n")
        
        # Para AJAX, devolvemos JSON con error
        return jsonify({
            'status': 'error',
            'message': "Error en la base de datos. Verifique los datos de Programación."
        }), 500

    

    
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

    return redirect(url_for('Administrador.ver_estudiantes_curso'))


@Administrador_bp.route('/citacion')
def citacion():
    return render_template('Administrador/Citacion.html')

@Administrador_bp.route('/citacion/registro', methods=['POST'])
@login_required  # <--- Solo permite acceso a usuarios logueados (Docente/Admin)
def registrar_citacion():
    try:
        # El ID del usuario que ENVÍA la citación se obtiene directamente
        enviado_por_id = current_user.ID_Usuario 

        # 1. Obtener datos del formulario con los nombres CORRECTOS del HTML:
        fecha_str = request.form.get('date')          # 👈 CORREGIDO: antes era 'Fecha'
        correo = request.form.get('email')            # 👈 CORREGIDO: antes era 'Correo'
        asunto = request.form.get('Asunto')           # ESTE ESTABA CORRECTO
        redaccion = request.form.get('message')       # 👈 CORREGIDO: antes era 'RedaccionCitacion'
        estado = request.form.get('Estado', 'Pendiente')
        
        # Validación de campos mínimos
        if not fecha_str or not correo or not asunto or not redaccion:
            return jsonify({'success': False, 'error': 'Faltan campos obligatorios (Fecha, Correo, Asunto o Redacción).'}), 400

        # 2. Búsqueda del ID del Destinatario (ID_Usuario) por Correo
        usuario_citado_obj = Usuario.query.filter_by(Correo=correo).first()
        
        if not usuario_citado_obj:
            return jsonify({'success': False, 'error': f'No se encontró un usuario registrado con el correo: {correo}'}), 400
        
        id_usuario_citado = usuario_citado_obj.ID_Usuario
        fecha_dt = datetime.strptime(fecha_str, '%Y-%m-%d')
        
        # 3. Crear y guardar la citación (Los nombres de las columnas sí deben ser los del modelo)
        nueva_citacion = Citaciones(
            Fecha=fecha_dt,
            Correo=correo,
            Asunto=asunto,
            RedaccionCitacion=redaccion, # El valor de 'redaccion' (que viene de name="message") se asigna aquí
            ID_Usuario=id_usuario_citado, 
            EnviadoPor=enviado_por_id,    
            Estado=estado
        )
        
        db.session.add(nueva_citacion)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Citación guardada exitosamente.'})

    except Exception as e:
        db.session.rollback()
        # Puedes imprimir el error en la consola del servidor para depuración
        print(f"Error al registrar citación: {e}") 
        return jsonify({'success': False, 'error': f'Error interno del servidor: {str(e)}'}), 500
    
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

    # Curso real (si viene desde otra vista)
    curso_id_real = request.args.get('curso_id', type=int)
    # Enviar a la plantilla
    return render_template('Administrador/detallesmateria.html', curso=curso_id, materia=materia, curso_id_real=curso_id_real)


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

@Administrador_bp.route('/evaluaciones')
def evaluaciones():
    return render_template('Administrador/evaluaciones.html')

@Administrador_bp.route('/informe')
def informe():
    return render_template('Administrador/informe.html')

@Administrador_bp.route('/informe/<int:curso_id>')
def informe_curso(curso_id):
    curso = Curso.query.get(curso_id)
    # Si no existe por ID directo, intentar mapear 1101 -> grado=11, grupo=1/01/A
    if not curso and isinstance(curso_id, int) and curso_id >= 100:
        grado_calc = curso_id // 100
        grupo_calc = curso_id % 100
        grupo_candidatos = [str(grupo_calc), f"{grupo_calc:02d}"]
        letra_map = {1: 'A', 2: 'B', 3: 'C', 4: 'D', 5: 'E'}
        if grupo_calc in letra_map:
            grupo_candidatos.append(letra_map[grupo_calc])
        for g in grupo_candidatos:
            curso = Curso.query.filter(
                or_(Curso.Grado == str(grado_calc), Curso.Grado == grado_calc),
                or_(Curso.Grupo == g, Curso.Grupo == int(g)) if g.isdigit() else (Curso.Grupo == g)
            ).first()
            if curso:
                break
        if not curso:
            return render_template('Administrador/informe.html', curso_id=curso_id, curso_nombre=str(curso_id))
        curso_id = curso.ID_Curso
    return render_template('Administrador/informe.html', curso_id=curso_id, curso_nombre=f"{curso.Grado}{curso.Grupo}")

@Administrador_bp.route('/informe/datos', methods=['GET'])
def informe_datos():
    try:
        curso_id = request.args.get('curso_id', type=int)
        periodo_num = request.args.get('periodo', type=int)
        if not curso_id:
            return jsonify({"success": False, "error": "curso_id requerido"}), 400

        # Intentar mapear si no hay matrículas para ese ID (por si llega como 1101)
        est_ids = [row.ID_Estudiante for row in Matricula.query.with_entities(Matricula.ID_Estudiante).filter_by(ID_Curso=curso_id).all()]
        if not est_ids and isinstance(curso_id, int) and curso_id >= 100:
            grado_calc = curso_id // 100
            grupo_calc = curso_id % 100
            grupo_candidatos = [str(grupo_calc), f"{grupo_calc:02d}"]
            letra_map = {1: 'A', 2: 'B', 3: 'C', 4: 'D', 5: 'E'}
            if grupo_calc in letra_map:
                grupo_candidatos.append(letra_map[grupo_calc])
            curso_alt = None
            for g in grupo_candidatos:
                curso_alt = Curso.query.filter(
                    or_(Curso.Grado == str(grado_calc), Curso.Grado == grado_calc),
                    or_(Curso.Grupo == g, Curso.Grupo == int(g)) if g.isdigit() else (Curso.Grupo == g)
                ).first()
                if curso_alt:
                    break
            if curso_alt:
                curso_id = curso_alt.ID_Curso
                est_ids = [row.ID_Estudiante for row in Matricula.query.with_entities(Matricula.ID_Estudiante).filter_by(ID_Curso=curso_id).all()]

        fecha_ini = fecha_fin = None
        if periodo_num:
            per = Periodo.query.filter_by(NumeroPeriodo=periodo_num).order_by(Periodo.Anio.desc()).first()
            if per and per.FechaInicial and per.FechaFinal:
                fecha_ini, fecha_fin = per.FechaInicial, per.FechaFinal

        q_notas = db.session.query(
            Asignatura.Nombre.label('asignatura'),
            func.avg(Nota_Calificaciones.Promedio_Final).label('prom')
        ).join(Asignatura, Asignatura.ID_Asignatura == Nota_Calificaciones.ID_Asignatura)
        q_notas = q_notas.filter(Nota_Calificaciones.ID_Estudiante.in_(est_ids))
        if periodo_num:
            q_notas = q_notas.filter(Nota_Calificaciones.Periodo == periodo_num)
        rendimiento = [
            {"asignatura": n.asignatura, "promedio": round(float(n.prom or 0), 2)}
            for n in q_notas.group_by(Asignatura.Nombre).all()
        ]

        q_asist = (
            db.session.query(Detalle_Asistencia.Estado_Asistencia, func.count().label('cnt'))
            .join(Asistencia, Asistencia.ID_Asistencia == Detalle_Asistencia.ID_Asistencia)
            .join(Programacion, Programacion.ID_Programacion == Asistencia.ID_Programacion)
            .filter(Programacion.ID_Curso == curso_id)
        )
        if est_ids:
            q_asist = q_asist.filter(Detalle_Asistencia.ID_Estudiante.in_(est_ids))
        if fecha_ini and fecha_fin:
            q_asist = q_asist.filter(Asistencia.Fecha.between(fecha_ini, fecha_fin))
        asist_rows = q_asist.group_by(Detalle_Asistencia.Estado_Asistencia).all()
        asistencia = {"Presente": 0, "Ausente": 0, "Justificado": 0}
        for estado, cnt in asist_rows:
            if estado in asistencia:
                asistencia[estado] = int(cnt)

        linea_disciplina = []
        periodos = Periodo.query.order_by(Periodo.NumeroPeriodo).all()
        for p in periodos:
            if periodo_num and p.NumeroPeriodo != periodo_num:
                continue
            q_obs = db.session.query(func.count(Observacion.ID_Observacion))
            if est_ids:
                q_obs = q_obs.filter(Observacion.ID_Estudiante.in_(est_ids))
            q_obs = q_obs.filter(Observacion.Tipo == 'Convivencial')
            if p.FechaInicial and p.FechaFinal:
                q_obs = q_obs.filter(Observacion.Fecha.between(p.FechaInicial, p.FechaFinal))
            cant = q_obs.scalar() or 0
            linea_disciplina.append({"periodo": p.NumeroPeriodo, "observaciones": int(cant)})

        # Datos extra para resumen
        curso_obj = Curso.query.get(curso_id)
        curso_label = f"{curso_obj.Grado}{curso_obj.Grupo}" if curso_obj else str(curso_id)
        est_count = len(est_ids)

        return jsonify({
            "success": True,
            "rendimiento": rendimiento,
            "asistencia": asistencia,
            "disciplina": linea_disciplina,
            "curso_label": curso_label,
            "est_count": est_count
        })
    except Exception as e:
        print('Error en /informe/datos:', e)
        return jsonify({"success": False, "error": str(e)}), 500

@Administrador_bp.route('/informe/estudiantes', methods=['GET'])
def informe_estudiantes():
    try:
        curso_id = request.args.get('curso_id', type=int)
        periodo_num = request.args.get('periodo', type=int)
        if not curso_id:
            return jsonify({"success": False, "error": "curso_id requerido"}), 400

        # Mapear 1101 -> ID_Curso si aplica
        est_ids = [row.ID_Estudiante for row in Matricula.query.with_entities(Matricula.ID_Estudiante).filter_by(ID_Curso=curso_id).all()]
        if not est_ids and isinstance(curso_id, int) and curso_id >= 100:
            grado_calc = curso_id // 100
            grupo_calc = curso_id % 100
            grupo_candidatos = [str(grupo_calc), f"{grupo_calc:02d}"]
            letra_map = {1: 'A', 2: 'B', 3: 'C', 4: 'D', 5: 'E'}
            if grupo_calc in letra_map:
                grupo_candidatos.append(letra_map[grupo_calc])
            curso_alt = None
            for g in grupo_candidatos:
                curso_alt = Curso.query.filter(
                    or_(Curso.Grado == str(grado_calc), Curso.Grado == grado_calc),
                    or_(Curso.Grupo == g, Curso.Grupo == int(g)) if g.isdigit() else (Curso.Grupo == g)
                ).first()
                if curso_alt:
                    break
            if curso_alt:
                curso_id = curso_alt.ID_Curso
                est_ids = [row.ID_Estudiante for row in Matricula.query.with_entities(Matricula.ID_Estudiante).filter_by(ID_Curso=curso_id).all()]

        # Listado base de estudiantes
        estudiantes = db.session.query(Usuario.ID_Usuario, Usuario.Nombre, Usuario.Apellido).join(Matricula, Matricula.ID_Estudiante == Usuario.ID_Usuario).filter(Matricula.ID_Curso == curso_id, Usuario.Rol == 'Estudiante').order_by(Usuario.Apellido, Usuario.Nombre).all()

        # Ventana de fechas si hay período
        fecha_ini = fecha_fin = None
        if periodo_num:
            per = Periodo.query.filter_by(NumeroPeriodo=periodo_num).order_by(Periodo.Anio.desc()).first()
            if per and per.FechaInicial and per.FechaFinal:
                fecha_ini, fecha_fin = per.FechaInicial, per.FechaFinal

        # Asistencia por estudiante
        q_asist = db.session.query(Detalle_Asistencia.ID_Estudiante, Detalle_Asistencia.Estado_Asistencia, func.count().label('cnt')) \
            .join(Asistencia, Asistencia.ID_Asistencia == Detalle_Asistencia.ID_Asistencia) \
            .join(Programacion, Programacion.ID_Programacion == Asistencia.ID_Programacion) \
            .filter(Programacion.ID_Curso == curso_id)
        if est_ids:
            q_asist = q_asist.filter(Detalle_Asistencia.ID_Estudiante.in_(est_ids))
        if fecha_ini and fecha_fin:
            q_asist = q_asist.filter(Asistencia.Fecha.between(fecha_ini, fecha_fin))
        q_asist = q_asist.group_by(Detalle_Asistencia.ID_Estudiante, Detalle_Asistencia.Estado_Asistencia).all()
        asist_map = {}
        for ide, est, cnt in q_asist:
            if ide not in asist_map:
                asist_map[ide] = {"Presente": 0, "Ausente": 0, "Justificado": 0}
            if est in asist_map[ide]:
                asist_map[ide][est] = int(cnt)

        # Observaciones convivenciales por estudiante
        q_obs = db.session.query(Observacion.ID_Estudiante, func.count(Observacion.ID_Observacion)) \
            .filter(Observacion.ID_Estudiante.in_(est_ids)) \
            .filter(Observacion.Tipo == 'Convivencial')
        if fecha_ini and fecha_fin:
            q_obs = q_obs.filter(Observacion.Fecha.between(fecha_ini, fecha_fin))
        q_obs = q_obs.group_by(Observacion.ID_Estudiante).all()
        obs_map = {row[0]: int(row[1]) for row in q_obs}

        items = []
        for e in estudiantes:
            a = asist_map.get(e.ID_Usuario, {"Presente": 0, "Ausente": 0, "Justificado": 0})
            items.append({
                "id": e.ID_Usuario,
                "nombre": f"{e.Apellido} {e.Nombre}",
                "asistencias": a.get("Presente", 0),
                "fallas": a.get("Ausente", 0),
                "retardos": 0,
                "observaciones": obs_map.get(e.ID_Usuario, 0)
            })

        return jsonify({"success": True, "items": items})
    except Exception as e:
        print('Error en /informe/estudiantes:', e)
        return jsonify({"success": False, "error": str(e)}), 500
    

@Administrador_bp.route('/comunicacion2')
def comunicacion2():
    return render_template('Administrador/Comunicación2.html')

@Administrador_bp.route('/config3/datos', methods=['GET'])
def config3_datos():
    try:
        curso_id = request.args.get('curso_id', type=int)
        asignatura_id = request.args.get('asignatura_id', type=int)
        periodo_num = request.args.get('periodo', type=int)
        if not curso_id:
            return jsonify({"success": False, "error": "curso_id requerido"}), 400

        est_ids = [row.ID_Estudiante for row in Matricula.query.with_entities(Matricula.ID_Estudiante).filter_by(ID_Curso=curso_id).all()]
        if not est_ids and isinstance(curso_id, int) and curso_id >= 100:
            grado_calc = curso_id // 100
            grupo_calc = curso_id % 100
            grupo_candidatos = [str(grupo_calc), f"{grupo_calc:02d}"]
            letra_map = {1: 'A', 2: 'B', 3: 'C', 4: 'D', 5: 'E'}
            if grupo_calc in letra_map:
                grupo_candidatos.append(letra_map[grupo_calc])
            curso_alt = None
            for g in grupo_candidatos:
                curso_alt = Curso.query.filter(
                    or_(Curso.Grado == str(grado_calc), Curso.Grado == grado_calc),
                    or_(Curso.Grupo == g, Curso.Grupo == int(g)) if g.isdigit() else (Curso.Grupo == g)
                ).first()
                if curso_alt:
                    break
            if curso_alt:
                curso_id = curso_alt.ID_Curso
                est_ids = [row.ID_Estudiante for row in Matricula.query.with_entities(Matricula.ID_Estudiante).filter_by(ID_Curso=curso_id).all()]

        q_est = (
            db.session.query(Usuario.ID_Usuario, Usuario.Nombre, Usuario.Apellido, Usuario.NumeroDocumento)
            .join(Matricula, Matricula.ID_Estudiante == Usuario.ID_Usuario)
            .filter(Matricula.ID_Curso == curso_id, Usuario.Rol == 'Estudiante')
            .order_by(Usuario.Apellido, Usuario.Nombre)
        )
        est_rows = q_est.all()
        if not est_rows:
            return jsonify({"success": True, "items": []})

        q_notas = db.session.query(
            Nota_Calificaciones.ID_Estudiante,
            func.avg(Nota_Calificaciones.Promedio_Final).label('prom')
        )
        if est_ids:
            q_notas = q_notas.filter(Nota_Calificaciones.ID_Estudiante.in_(est_ids))
        if asignatura_id:
            q_notas = q_notas.filter(Nota_Calificaciones.ID_Asignatura == asignatura_id)
        if periodo_num:
            q_notas = q_notas.filter(Nota_Calificaciones.Periodo == periodo_num)
        q_notas = q_notas.group_by(Nota_Calificaciones.ID_Estudiante).all()
        prom_map = {row[0]: float(row[1]) if row[1] is not None else None for row in q_notas}

        def nivel_y_obs(prom):
            if prom is None:
                return ('-', '')
            if prom >= 4.6:
                return ('Superior', 'excelente desempeño')
            if prom >= 4.0:
                return ('Alto', 'muy buena participación')
            if prom >= 3.0:
                return ('Básico', 'debe reforzar contenidos')
            return ('Bajo', 'necesita apoyo académico')

        periodo_label = str(periodo_num) if periodo_num else ''
        items = []
        for idx, e in enumerate(est_rows, start=1):
            prom = prom_map.get(e.ID_Usuario)
            niv, obs = nivel_y_obs(prom)
            items.append({
                "detalles": idx,
                "nombre": f"{e.Nombre} {e.Apellido}",
                "documento": e.NumeroDocumento or '',
                "promedio": round(prom, 2) if prom is not None else None,
                "nivel": niv,
                "observacion": obs,
                "periodo": periodo_label
            })

        return jsonify({"success": True, "items": items})
    except Exception as e:
        print('Error en /config3/datos:', e)
        return jsonify({"success": False, "error": str(e)}), 500
