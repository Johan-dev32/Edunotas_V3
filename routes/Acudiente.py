from flask import Blueprint, render_template, request, redirect, url_for, flash
from Controladores.models import db, Usuario, Curso, Periodo, Asignatura, Docente_Asignatura, Programacion, Cronograma_Actividades
import os

from decimal import Decimal
#Definir el Blueprint para el administardor
Acudiente_bp = Blueprint('Acudiente', __name__, url_prefix='/acudiente')