from flask import Blueprint, render_template, request, redirect, url_for, flash
from Controladores.models import db, Usuario, Curso, Periodo, Asignatura, Docente_Asignatura, Programacion, Cronograma_Actividades
import os

from decimal import Decimal
#Definir el Blueprint para el administardor
Estudiante_bp = Blueprint('Estudiante', __name__, url_prefix='/estudiante')

@Estudiante_bp.route('/paginainicio')
def paginainicio():
    return render_template('estudiante/Paginainicio.html')