from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, abort
from flask_login import login_required, current_user
from Controladores.models import db, Usuario, Curso, Periodo, Asignatura, Docente_Asignatura, Programacion, Cronograma_Actividades, Notificacion, Matricula, Observacion, Acudiente
import os

from decimal import Decimal
#Definir el Blueprint para el administardor
Acudiente_bp = Blueprint('Acudiente', __name__, url_prefix='/acudiente')


@Acudiente_bp.route('/paginainicio')
def paginainicio():
    return render_template('Acudiente/Paginainicio_Acudiente.html')

# ---------------- NOTIFICACIONES ACUDIENTE----------------



@Acudiente_bp.route('/ver_notas')
def ver_notas():
    return render_template('Acudiente/ver_notas.html')

@Acudiente_bp.route('/ver_notas2')
def ver_notas2():
    return render_template('Acudiente/ver_notas2.html')

@Acudiente_bp.route('/ver_citaciones')
def ver_citaciones():
    return render_template('Acudiente/ver_citaciones.html')

@Acudiente_bp.route('/ver_citaciones2')
def ver_citaciones2():
    return render_template('Acudiente/ver_citaciones2.html')

@Acudiente_bp.route('/inasistencias_justificadas')
def inasistencias_justificadas():
    return render_template('Acudiente/InasistenciasJustificadas.html')

@Acudiente_bp.route('/informes_academicos')
def informes_academicos():
    return render_template('Acudiente/InformesAcademicos.html')

@Acudiente_bp.route('/comunicados')
def comunicados():
    return render_template('Acudiente/Comunicados.html')


@Acudiente_bp.route('/observador')
def ver_observador_estudiante():
    try:
        # Aquí la función ya está definida y disponible
        estudiante_a_cargo_id = Acudiente(current_user.ID_Usuario) 
    except:
        # Si la función lanza el ValueError, se captura aquí y se redirige
        return render_template('Acudiente/ObservadorEstudiante.html', mensaje="No tienes un estudiante asociado.")

    observaciones = (
        db.session.query(Observacion, Usuario, Curso)
        .join(Matricula, Observacion.ID_Matricula == Matricula.ID_Matricula)
        .join(Usuario, Matricula.ID_Estudiante == Usuario.ID_Usuario)
        .join(Curso, Matricula.ID_Curso == Curso.ID_Curso)
        .filter(Matricula.ID_Estudiante == estudiante_a_cargo_id)
        .order_by(Observacion.Fecha.desc())
        .all()
    )
    
    return render_template(
        'Acudiente/ObservadorEstudiante.html',
        observaciones=observaciones
    )


@Acudiente_bp.route('/observador/<int:anotacion_id>')
def ver_observador_estudiante2(anotacion_id):
    try:
        # Aquí la función ya está definida y disponible
        estudiante_a_cargo_id = Acudiente(current_user.ID_Usuario) 
    except:
        # Se detiene la solicitud y se devuelve el código 403 (Forbidden)
        # Esto soluciona el error de "NameError" (subrayado rojo/gris)
        abort(403)

    anotacion = (
        db.session.query(Observacion, Usuario, Curso)
        .join(Matricula, Observacion.ID_Matricula == Matricula.ID_Matricula)
        .join(Usuario, Matricula.ID_Estudiante == Usuario.ID_Usuario)
        .join(Curso, Matricula.ID_Curso == Curso.ID_Curso)
        .filter(
            Observacion.ID_Observacion == anotacion_id, 
            Matricula.ID_Estudiante == estudiante_a_cargo_id
        )
        .first()
    )

    if not anotacion:
        # Se detiene la solicitud y se devuelve el código 404 (Not Found)
        # Esto soluciona el error de "NameError" (subrayado rojo/gris)
        abort(404) 

    return render_template(
        'Acudiente/ObservadorEstudiante2.html',
        anotacion=anotacion
    )

@Acudiente_bp.route('/historial_academico')
def historial_academico():
    return render_template('Acudiente/Historial_academico.html')

@Acudiente_bp.route('/historial_academico2')
def historial_academico2():
    return render_template('Acudiente/historial_academico2.html')

@Acudiente_bp.route('/manual')
def manual():
    return render_template('Acudiente/ManualUsuario.html')

@Acudiente_bp.route('/comunicacion')
def comunicacion():
    return render_template('Acudiente/Comunicacion.html')

@Acudiente_bp.route('/horarios')
def horarios():
    return render_template('Acudiente/Horarios.html')

@Acudiente_bp.route('/circulares')
def circulares():
    return render_template('Acudiente/Circulares.html')