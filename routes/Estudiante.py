from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from Controladores.models import db, Usuario, Curso, Periodo, Asignatura, Docente_Asignatura, Programacion, Cronograma_Actividades, Notificacion
import os

from decimal import Decimal
#Definir el Blueprint para el administardor
Estudiante_bp = Blueprint('Estudiante', __name__, url_prefix='/estudiante')

@Estudiante_bp.route('/paginainicio')
def paginainicio():
    return render_template('Estudiante/Paginainicio_Estudiante.html')

@Estudiante_bp.route('/subidaevidencias')
def subidaevidencias():
    return render_template('Estudiante/SubidaEvidencias.html')

@Estudiante_bp.route('/verhorario')
def verhorario():
    return render_template('Estudiante/VerHorario.html')

@Estudiante_bp.route('/vernotas')
def vernotas():
    return render_template('Estudiante/VerNotas.html')

@Estudiante_bp.route('/materialestudiante')
def materialestudiante():
    return render_template('Estudiante/MaterialEstudiante.html')

@Estudiante_bp.route('/evaluaciones')
def evaluaciones():
    return render_template('Estudiante/Evaluaciones.html')

@Estudiante_bp.route('/tutorias')
def tutorias():
    return render_template('Estudiante/Tutorias.html')

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
def tareas_actividades():
    return render_template('Estudiante/TareasActividades.html')
