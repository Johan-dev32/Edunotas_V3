from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from Controladores.models import db, Docente_Asignatura, Programacion, Asistencia, Detalle_Asistencia, Actividad, Actividad_Estudiante, Observacion
import os

from decimal import Decimal
#Definir el Blueprint para el administardor
Docente_bp = Blueprint('Docente', __name__, url_prefix='/docente')

@Docente_bp.route('/paginainicio')
def paginainicio():
    return render_template('Docentes/Paginainicio.html')

@Docente_bp.route('/perfil')
@login_required
def perfil():
    return render_template('Docentes/perfil.html', usuario=current_user)