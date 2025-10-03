from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
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