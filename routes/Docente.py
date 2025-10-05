from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from flask_mail import Message
from Controladores.models import db, Docente_Asignatura, Programacion, Asistencia, Detalle_Asistencia, Actividad, Actividad_Estudiante, Observacion
import os

from decimal import Decimal
#Definir el Blueprint para el administardor
Docente_bp = Blueprint('Docente', __name__, url_prefix='/docente')

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

@Docente_bp.route('/tareas_actividades')
def tareas_actividades():
    return render_template('Docentes/Registrar_Tareas_Actividades.html')

@Docente_bp.route('/tareas_actividades2')
def tareas_actividades2():
    return render_template('Docentes/Registrar_Tareas_Actividades2.html')

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

