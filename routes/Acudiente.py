from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, abort
from flask_login import login_required, current_user
from Controladores.models import db, Usuario, Curso, Periodo, Asignatura, Docente_Asignatura, Programacion, Cronograma_Actividades, Notificacion, Acudiente, Nota_Calificaciones, Citaciones, Observacion, Matricula
from sqlalchemy import or_, func
import os
import unicodedata

from decimal import Decimal
#Definir el Blueprint para el administardor
Acudiente_bp = Blueprint('Acudiente', __name__, url_prefix='/acudiente')


@Acudiente_bp.route('/paginainicio')
def paginainicio():
    return render_template('Acudiente/Paginainicio_Acudiente.html')

# ---------------- NOTIFICACIONES ACUDIENTE----------------



@Acudiente_bp.route('/ver_notas')
@login_required
def ver_notas():
    return render_template('Acudiente/ver_notas.html')

@Acudiente_bp.route('/ver_notas2')
@login_required
def ver_notas2():
    materia_nombre = request.args.get('materia')
    if not materia_nombre:
        flash('Debe seleccionar una materia.', 'warning')
        return redirect(url_for('Acudiente.ver_notas'))

    # Resolver asignatura por nombre (insensible a acentos y mayúsculas)
    def _normalize(s):
        if not s:
            return ''
        return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn').strip().upper()

    materia_norm = _normalize(materia_nombre)
    asignatura = None
    for asig in Asignatura.query.all():
        if _normalize(asig.Nombre) == materia_norm:
            asignatura = asig
            break
    if not asignatura:
        flash('La materia seleccionada no existe.', 'danger')
        return redirect(url_for('Acudiente.ver_notas'))

    # Obtener estudiante asociado al acudiente actual
    relaciones = Acudiente.query.filter_by(ID_Usuario=current_user.ID_Usuario, Estado='Activo').all()
    estudiante = None
    registros = []
    if not relaciones:
        flash('No tiene estudiantes asociados.', 'warning')
    else:
        # Por ahora tomamos el primer estudiante asociado
        estudiante_id = relaciones[0].ID_Estudiante
        estudiante = Usuario.query.get(estudiante_id)

        # Consultar notas del estudiante para la asignatura seleccionada, ordenadas por período
        registros = Nota_Calificaciones.query.filter_by(
            ID_Estudiante=estudiante_id,
            ID_Asignatura=asignatura.ID_Asignatura
        ).order_by(Nota_Calificaciones.Periodo.asc()).all()

    # Calcular promedio general (solo promedios no nulos)
    promedios_validos = [r.Promedio_Final for r in registros if getattr(r, 'Promedio_Final', None) is not None]
    promedio_general = round(sum(promedios_validos) / len(promedios_validos), 2) if promedios_validos else None

    return render_template(
        'Acudiente/ver_notas2.html',
        materia=materia_nombre,
        asignatura_id=asignatura.ID_Asignatura,
        estudiante=estudiante,
        notas=registros,
        promedio_general=promedio_general
    )

@Acudiente_bp.route('/ver_citaciones')
@login_required
def ver_citaciones():
    relaciones = Acudiente.query.filter_by(ID_Usuario=current_user.ID_Usuario, Estado='Activo').all()
    citaciones = []
    estudiante = None

    if not relaciones:
        flash('No tiene estudiantes asociados.', 'warning')
        return render_template('Acudiente/ver_citaciones.html', estudiante=None, citaciones=[])

    # Permitir override explícito
    override_id = request.args.get('estudiante_id', type=int)
    ids_relacionados = [rel.ID_Estudiante for rel in relaciones]

    if override_id and override_id in ids_relacionados:
        estudiante = Usuario.query.get(override_id)
        correos = [estudiante.Correo] if estudiante and estudiante.Correo else []
        ids = [override_id]
    else:
        # Tomar el primero como seleccionado por defecto para cabecera
        estudiante = Usuario.query.get(ids_relacionados[0])
        # Buscar por todos los hijos asociados
        hijos = Usuario.query.filter(Usuario.ID_Usuario.in_(ids_relacionados)).all()
        ids = [h.ID_Usuario for h in hijos]
        correos = [h.Correo for h in hijos if h.Correo]

    # Construir consulta por múltiples IDs/correos (correo insensible a mayúsculas)
    condiciones = []
    if ids:
        condiciones.append(Citaciones.ID_Usuario.in_(ids))
    if correos:
        condiciones.extend([func.lower(Citaciones.Correo) == c.lower() for c in correos])

    if condiciones:
        citaciones = (
            Citaciones.query
            .filter(or_(*condiciones))
            .order_by(Citaciones.Fecha.desc())
            .all()
        )

    return render_template('Acudiente/ver_citaciones.html', estudiante=estudiante, citaciones=citaciones)

@Acudiente_bp.route('/ver_citaciones2')
@login_required
def ver_citaciones2():
    citacion_id = request.args.get('id', type=int)
    if not citacion_id:
        flash('Citación no especificada.', 'warning')
        return redirect(url_for('Acudiente.ver_citaciones'))

    # Obtener todos los estudiantes asociados
    relaciones = Acudiente.query.filter_by(ID_Usuario=current_user.ID_Usuario, Estado='Activo').all()
    if not relaciones:
        flash('No tiene estudiantes asociados.', 'warning')
        return redirect(url_for('Acudiente.ver_citaciones'))

    ids_estudiantes = [rel.ID_Estudiante for rel in relaciones]
    estudiantes = Usuario.query.filter(Usuario.ID_Usuario.in_(ids_estudiantes)).all()
    correos_est = [e.Correo for e in estudiantes if e.Correo]

    # Traer citación
    citacion = Citaciones.query.get(citacion_id)
    if not citacion:
        flash('Citación no encontrada.', 'danger')
        return redirect(url_for('Acudiente.ver_citaciones'))

    # Validar pertenencia
    pertenece = (citacion.ID_Usuario in ids_estudiantes) or \
                (citacion.Correo and any(citacion.Correo.lower() == c.lower() for c in correos_est))
    if not pertenece:
        flash('No tiene permisos para ver esta citación.', 'danger')
        return redirect(url_for('Acudiente.ver_citaciones'))

    # Estudiante seleccionado (para cabecera): por ID_Usuario si coincide, si no por correo
    estudiante = next((e for e in estudiantes if e.ID_Usuario == citacion.ID_Usuario), None)
    if not estudiante and citacion.Correo:
        estudiante = next((e for e in estudiantes if e.Correo and e.Correo.lower() == citacion.Correo.lower()), None)

    return render_template('Acudiente/ver_citaciones2.html', estudiante=estudiante, citacion=citacion)

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