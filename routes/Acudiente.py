from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from Controladores.models import db, Usuario, Curso, Periodo, Asignatura, Docente_Asignatura, Programacion, Cronograma_Actividades, Notificacion
import os

from decimal import Decimal
#Definir el Blueprint para el administardor
Acudiente_bp = Blueprint('Acudiente', __name__, url_prefix='/acudiente')

@Acudiente_bp.route('/paginainicio')
def paginainicio():
    return render_template('Acudiente/Paginainicio_Acudiente.html')

@Acudiente_bp.route('/ver_notas_e_informes')
def ver_notas_e_informes():
    return render_template('Acudiente/Notas_Informes.html')

@Acudiente_bp.route('/ver_citaciones')
def ver_citaciones():
    return render_template('Acudiente/ver_citaciones.html')

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

@Acudiente_bp.route('/historial_academico')
def historial_academico():
    return render_template('Acudiente/Historial_academico.html')