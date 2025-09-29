from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import generate_password_hash
from Controladores.models import db, Usuario, Curso, Periodo, Asignatura, Docente_Asignatura, Programacion, Cronograma_Actividades
import os

from decimal import Decimal
#Definir el Blueprint para el administardor
Administrador_bp = Blueprint('Administrador', __name__, url_prefix='/administrador')


# ----------------- RUTAS DE INICIO -----------------
@Administrador_bp.route('/paginainicio')
def paginainicio():
    return render_template('Administrador/Paginainicio.html')


@Administrador_bp.route('/perfil')
@login_required
def perfil():
    return render_template('Administrador/perfil.html', usuario=current_user)


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
            Calle=curso,
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


@Administrador_bp.route('/materialapoyo')
def materialapoyo():
    return render_template('Administrador/MaterialApoyo.html')


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


# ----------------- SUB-PÁGINAS -----------------
@Administrador_bp.route('/materialapoyo2')
def materialapoyo2():
    return render_template('Administrador/MaterialApoyo2.html')


@Administrador_bp.route('/registrotutorias2')
def registrotutorias2():
    return render_template('Administrador/RegistroTutorías2.html')