from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from Controladores.models import db, Matricula, Actividad, Curso, Periodo, Asignatura, Programacion, Actividad_Estudiante, Notificacion
import os

from decimal import Decimal
#Definir el Blueprint para el administardor
Estudiante_bp = Blueprint('Estudiante', __name__, url_prefix='/estudiante')

@Estudiante_bp.route('/paginainicio')
def paginainicio():
    return render_template('Estudiante/Paginainicio_Estudiante.html')

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
@login_required
def tareas_actividades():
    try:
        # Buscar las matrículas del estudiante actual
        matriculas = Matricula.query.filter_by(ID_Estudiante=current_user.ID_Usuario).all()
        cursos_ids = [m.ID_Curso for m in matriculas]

        # Buscar actividades relacionadas con sus cursos
        actividades = []
        if cursos_ids:
            actividades = Actividad.query.filter(Actividad.ID_Curso.in_(cursos_ids)).all()

        return render_template('Estudiante/TareasActividades.html', actividades=[(a, None) for a in actividades])
    except Exception as e:
        flash(f"Error al cargar actividades: {e}", "danger")
        return redirect(url_for('Estudiante.paginainicio'))
    
@Estudiante_bp.route('/subida_evidencias/<int:id_actividad>')
@login_required
def subida_evidencias(id_actividad):
    try:
        actividad = Actividad.query.get(id_actividad)
        if not actividad:
            flash("Actividad no encontrada.", "warning")
            return redirect(url_for('Estudiante.tareas_actividades'))

        return render_template('Estudiante/SubidaEvidencias.html',
                               actividad_id=actividad.ID_Actividad,
                               titulo_actividad=actividad.Titulo,
                               descripcion_actividad=actividad.Tipo,  # puedes reemplazar por otra descripción si la agregas
                               fecha_entrega=actividad.Fecha,
                               hora_entrega=None,
                               pdf_nombre=None)
    except Exception as e:
        flash(f"Error: {e}", "danger")
        return redirect(url_for('Estudiante.tareas_actividades'))
    
@Estudiante_bp.route('/enviar_evidencia/<int:id_actividad>', methods=['POST'])
@login_required
def enviar_evidencia(id_actividad):
    archivo = request.files.get('archivo')
    if not archivo:
        flash('Debes seleccionar un archivo.', 'warning')
        return redirect(url_for('Estudiante.subida_evidencias', id_actividad=id_actividad))
    
    upload_folder = os.path.join(os.getcwd(), 'static', 'uploads', 'evidencias')
    os.makedirs(upload_folder, exist_ok=True)
    filename = secure_filename(archivo.filename)
    archivo.save(os.path.join(upload_folder, filename))
    flash('Evidencia subida correctamente.', 'success')
    return redirect(url_for('Estudiante.tareas_actividades'))

@Estudiante_bp.route('/notas_consultar')
def notas_consultar():
    return render_template('Estudiante/NotasConsultar.html')

@Estudiante_bp.route('/notas_registro')
def notas_registro():
    return render_template('Estudiante/NotasRegistro.html')

@Estudiante_bp.route('/calculo_promedio')
def calculo_promedio():
    return render_template('Estudiante/CalculoPromedio.html')

@Estudiante_bp.route('/observador')
def observador():  
    return render_template('Estudiante/Observador.html')

@Estudiante_bp.route('/aprobacion_academica')
def aprobacion_academica():
    return render_template('Estudiante/AprobacionAcademica.html')

@Estudiante_bp.route('/citaciones')
def citaciones():
    return render_template('Estudiante/Citaciones.html')

@Estudiante_bp.route('/historial_academico')
def historial_academico():
    return render_template('Estudiante/HistorialAcademico.html')

@Estudiante_bp.route('/certificados')
def certificados():
    return render_template('Estudiante/Certificados.html')

@Estudiante_bp.route('/reportes_estudiante')
def reportes_estudiante():
    return render_template('Estudiante/ReportesEstudiante.html')

@Estudiante_bp.route('/manual')
def manual():
    return render_template('Estudiante/ManualUsuario.html')