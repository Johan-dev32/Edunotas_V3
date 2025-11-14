from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_required, current_user
from Controladores.models import db, Usuario, Curso, Periodo, Asignatura, Docente_Asignatura, Programacion, Cronograma_Actividades, Notificacion
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

@Acudiente_bp.route('/ver_observador_estudiante')
def ver_observador_estudiante():
    return render_template('Acudiente/ObservadorEstudiante.html')


@Acudiente_bp.route('/ver_observador_estudiante2')
def ver_observador_estudiante2():
    return render_template('Acudiente/ObservadorEstudiante2.html')

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