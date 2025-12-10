from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, abort
from flask_login import login_required, current_user
from Controladores.models import db, Usuario, Curso, Periodo, Asignatura, Docente_Asignatura, Programacion, Cronograma_Actividades, Notificacion, Acudiente, Nota_Calificaciones, Citaciones, Observacion, Matricula, Detalle_Asistencia
from sqlalchemy import or_, func
from datetime import datetime
import os
import unicodedata

from decimal import Decimal
#Definir el Blueprint para el administardor
Acudiente_bp = Blueprint('Acudiente', __name__, url_prefix='/acudiente')


@Acudiente_bp.route('/paginainicio')
def paginainicio():
    return render_template('Acudiente/Paginainicio_Acudiente.html')

# ---------------- INASISTENCIAS ACUDIENTE----------------
@Acudiente_bp.route('/inasistencias')
@login_required
def ver_inasistencias():
    # Buscar estudiantes asociados al acudiente
    relaciones = Acudiente.query.filter_by(ID_Usuario=current_user.ID_Usuario, Estado='Activo').all()
    if not relaciones:
        flash("No tiene estudiantes asociados.", "warning")
        return render_template("Acudiente/InasistenciasLista.html", inasistencias=[])

    estudiante_id = relaciones[0].ID_Estudiante

    faltas = Detalle_Asistencia.query.filter_by(
        ID_Estudiante=estudiante_id,
        Estado_Asistencia='Ausente'
    ).all()

    return render_template("Acudiente/InasistenciasLista.html", faltas=faltas)


@Acudiente_bp.route('/enviar_excusa/<int:id_detalle>', methods=['POST'])
@login_required
def enviar_excusa(id_detalle):
    detalle = Detalle_Asistencia.query.get_or_404(id_detalle)

    # validar que ese estudiante SI pertenece a este acudiente
    relacion = Acudiente.query.filter_by(
        ID_Usuario=current_user.ID_Usuario,
        ID_Estudiante=detalle.ID_Estudiante,
        Estado="Activo"
    ).first()

    if not relacion:
        abort(403)

    texto = request.form.get("texto_excusa")
    archivo = request.files.get("archivo_excusa")

    nombre_archivo = None
    if archivo and archivo.filename:
        carpeta = "static/excusas/"
        os.makedirs(carpeta, exist_ok=True)
        nombre_archivo = f"excusa_{id_detalle}_{archivo.filename}"
        archivo.save(os.path.join(carpeta, nombre_archivo))

    detalle.TextoExcusa = texto
    detalle.ArchivoExcusa = nombre_archivo
    detalle.FechaExcusa = datetime.now()
    detalle.ID_Acudiente = relacion.ID_Acudiente
    detalle.EstadoExcusa = "pendiente"

    db.session.commit()

    flash("Excusa enviada correctamente.", "success")
    return redirect(url_for('Acudiente.inasistencias_justificadas'))

@Acudiente_bp.route('/mis_excusas')
@login_required
def mis_excusas():
    relaciones = Acudiente.query.filter_by(ID_Usuario=current_user.ID_Usuario, Estado='Activo').all()
    if not relaciones:
        flash("No tiene estudiantes asociados.", "warning")
        return render_template("Acudiente/MisExcusas.html", excusas=[])

    estudiante_id = relaciones[0].ID_Estudiante

    excusas = Detalle_Asistencia.query.filter(
        Detalle_Asistencia.ID_Estudiante == estudiante_id,
        Detalle_Asistencia.TextoExcusa.isnot(None)
    ).order_by(Detalle_Asistencia.FechaExcusa.desc()).all()

    return render_template("Acudiente/MisExcusas.html", excusas=excusas)


# ---------------- NOTIFICACIONES ACUDIENTE----------------



@Acudiente_bp.route('/limpiar_duplicados')
@login_required
def limpiar_duplicados():
    # Función temporal para limpiar duplicados del acudiente actual
    relaciones = Acudiente.query.filter_by(ID_Usuario=current_user.ID_Usuario, Estado='Activo').all()
    
    if len(relaciones) > 1:
        print(f"DEBUG: Limpiando {len(relaciones)} relaciones del acudiente {current_user.ID_Usuario}")
        
        # Obtener todos los IDs de estudiantes
        estudiantes_ids = [rel.ID_Estudiante for rel in relaciones]
        from collections import Counter
        contador = Counter(estudiantes_ids)
        
        # Eliminar todas las relaciones duplicadas
        eliminadas = 0
        for estudiante_id, count in contador.items():
            if count > 1:
                # Obtener todas las relaciones para este estudiante, ordenadas por ID
                relaciones_estudiante = Acudiente.query.filter_by(
                    ID_Usuario=current_user.ID_Usuario,
                    ID_Estudiante=estudiante_id,
                    Estado='Activo'
                ).order_by(Acudiente.ID_Acudiente.asc()).all()
                
                # Mantener solo la primera, eliminar las demás
                for i in range(1, len(relaciones_estudiante)):
                    print(f"DEBUG: Eliminando relación ID {relaciones_estudiante[i].ID_Acudiente} con estudiante {estudiante_id}")
                    db.session.delete(relaciones_estudiante[i])
                    eliminadas += 1
        
        db.session.commit()
        print(f"DEBUG: Se eliminaron {eliminadas} relaciones duplicadas")
        flash(f'Se eliminaron {eliminadas} relaciones duplicadas correctamente.', 'success')
    else:
        flash('No se encontraron relaciones duplicadas.', 'info')
    
    return redirect(url_for('Acudiente.ver_notas'))

@Acudiente_bp.route('/api/asignaturas_disponibles')
@login_required
def api_asignaturas_disponibles():
    # Obtener todas las asignaturas que tienen notas registradas
    asignaturas_con_notas = db.session.query(Asignatura).join(Nota_Calificaciones).distinct().all()
    
    # Debug: mostrar todas las asignaturas encontradas
    print("DEBUG: Asignaturas encontradas en la base de datos:")
    for asig in asignaturas_con_notas:
        print(f"  - ID: {asig.ID_Asignatura}, Nombre: '{asig.Nombre}'")
    
    # Mapeo para traducir nombres
    traducciones_asignaturas = {
        'Artistic': 'Artística',
        'Mathematics': 'Matemáticas',
        'Science': 'Ciencias',
        'English': 'Inglés',
        'Social Studies': 'Estudios Sociales',
        'Physical Education': 'Educación Física',
        'Technology': 'Tecnología',
        'Religion': 'Religión',
        'Spanish': 'Español',
        'Music': 'Música',
        'Chemistry': 'Química',
        'Physics': 'Física',
        'Biology': 'Biología',
        'History': 'Historia',
        'Geography': 'Geografía',
        'Literature': 'Literatura',
        'Philosophy': 'Filosofía'
    }
    
    resultado = []
    nombres_vistos = set()  # Para evitar duplicados
    
    # Verificar si existe "Inglés" (con tilde) en la base de datos
    existe_ingles_con_tilde = any(asig.Nombre == 'Inglés' for asig in asignaturas_con_notas)
    print(f"DEBUG: ¿Existe 'Inglés' con tilde? {existe_ingles_con_tilde}")
    
    for asignatura in asignaturas_con_notas:
        # Si existe "Inglés" con tilde, ignorar completamente la asignatura "English"
        if existe_ingles_con_tilde and asignatura.Nombre == 'English':
            print(f"DEBUG: Ignorando asignatura 'English' (ID: {asignatura.ID_Asignatura}) porque existe 'Inglés'")
            continue  # Saltar esta asignatura
        
        # Traducir el nombre
        nombre_traducido = traducciones_asignaturas.get(asignatura.Nombre, asignatura.Nombre)
        
        # Solo agregar si no hemos visto este nombre traducido
        if nombre_traducido not in nombres_vistos:
            resultado.append({
                'id': asignatura.ID_Asignatura,
                'nombre': nombre_traducido,
                'nombre_original': asignatura.Nombre
            })
            nombres_vistos.add(nombre_traducido)
            print(f"DEBUG: Agregando '{nombre_traducido}' (ID: {asignatura.ID_Asignatura})")
        else:
            print(f"DEBUG: Ignorando duplicado '{nombre_traducido}' (ID: {asignatura.ID_Asignatura})")
    
    print(f"DEBUG: Total de asignaturas devueltas: {len(resultado)}")
    return jsonify(resultado)

@Acudiente_bp.route('/ver_notas')
@login_required
def ver_notas():
    return render_template('Acudiente/ver_notas.html')

@Acudiente_bp.route('/ver_notas2')
@login_required
def ver_notas2():
    # Mapeo para traducir nombres de asignaturas
    traducciones_asignaturas = {
        'Artistic': 'Artística',
        'Mathematics': 'Matemáticas',
        'Science': 'Ciencias',
        'English': 'Inglés',
        'Social Studies': 'Estudios Sociales',
        'Physical Education': 'Educación Física',
        'Technology': 'Tecnología',
        'Religion': 'Religión',
        'Spanish': 'Español',
        'Music': 'Música',
        'Chemistry': 'Química',
        'Physics': 'Física',
        'Biology': 'Biología',
        'History': 'Historia',
        'Geography': 'Geografía',
        'Literature': 'Literatura',
        'Philosophy': 'Filosofía'
    }
    
    # 1. Intentar recibir directamente el ID de la asignatura
    asignatura_id = request.args.get('asignatura_id', type=int)
    materia_nombre = request.args.get('materia')

    if asignatura_id:
        asignatura = Asignatura.query.get(asignatura_id)
        if not asignatura:
            flash('La materia seleccionada no existe.', 'danger')
            return redirect(url_for('Acudiente.ver_notas'))
        # Si el nombre no viene, usar el de la asignatura y traducirlo
        if not materia_nombre:
            materia_nombre = asignatura.Nombre
            # Traducir el nombre si existe en el mapeo
            materia_nombre = traducciones_asignaturas.get(materia_nombre, materia_nombre)
    else:
        # Compatibilidad: resolver por nombre (insensible a acentos y mayúsculas)
        if not materia_nombre:
            flash('Debe seleccionar una materia.', 'warning')
            return redirect(url_for('Acudiente.ver_notas'))

        # Traducir el nombre si viene por parámetro
        materia_nombre = traducciones_asignaturas.get(materia_nombre, materia_nombre)

        def _normalize(s):
            if not s:
                return ''
            return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn').strip().upper()

        materia_norm = _normalize(materia_nombre)
        materia_root = materia_norm.split()[0] if materia_norm else ''

        asignatura = None
        for asig in Asignatura.query.all():
            nombre_norm = _normalize(asig.Nombre)
            if nombre_norm.startswith(materia_norm) or nombre_norm.startswith(materia_root):
                asignatura = asig
                break

    if not asignatura:
        flash('La materia seleccionada no existe.', 'danger')
        return redirect(url_for('Acudiente.ver_notas'))

    # Obtener estudiante asociado al acudiente actual
    relaciones = Acudiente.query.filter_by(ID_Usuario=current_user.ID_Usuario, Estado='Activo').all()
    estudiante = None
    registros = []
    
    print(f"DEBUG: Relaciones encontradas para acudiente {current_user.ID_Usuario}: {len(relaciones)}")
    
    # Limpiar relaciones duplicadas si existen
    if len(relaciones) > 1:
        print("DEBUG: Se encontraron múltiples relaciones, limpiando duplicados...")
        # Obtener todos los IDs de estudiantes duplicados
        estudiantes_ids = [rel.ID_Estudiante for rel in relaciones]
        # Contar cuántas veces aparece cada estudiante
        from collections import Counter
        contador = Counter(estudiantes_ids)
        
        # Para cada estudiante que aparece más de una vez, mantener solo la primera relación
        for estudiante_id, count in contador.items():
            if count > 1:
                # Obtener todas las relaciones para este estudiante
                relaciones_estudiante = [rel for rel in relaciones if rel.ID_Estudiante == estudiante_id]
                # Mantener solo la primera, eliminar las demás
                for i in range(1, len(relaciones_estudiante)):
                    print(f"DEBUG: Eliminando relación duplicada con estudiante {estudiante_id}")
                    db.session.delete(relaciones_estudiante[i])
        
        db.session.commit()
        
        # Recargar relaciones después de limpiar
        relaciones = Acudiente.query.filter_by(ID_Usuario=current_user.ID_Usuario, Estado='Activo').all()
        print(f"DEBUG: Relaciones después de limpiar: {len(relaciones)}")
    
    if not relaciones:
        print("DEBUG: No hay relaciones - creando relación temporal con estudiante de ejemplo")
        # Buscar un estudiante existente para asociar temporalmente
        estudiante_ejemplo = Usuario.query.filter_by(Rol='Estudiante').first()
        if estudiante_ejemplo:
            # Crear relación temporal
            nueva_relacion = Acudiente(
                ID_Usuario=current_user.ID_Usuario,
                ID_Estudiante=estudiante_ejemplo.ID_Usuario,
                Estado='Activo'
            )
            db.session.add(nueva_relacion)
            db.session.commit()
            print(f"DEBUG: Relación temporal creada con estudiante {estudiante_ejemplo.Nombre} (ID: {estudiante_ejemplo.ID_Usuario})")
            relaciones = [nueva_relacion]
        else:
            flash('No hay estudiantes disponibles en el sistema.', 'danger')
            return redirect(url_for('Acudiente.ver_notas'))
    else:
        # Por ahora tomamos el primer estudiante asociado
        estudiante_id = relaciones[0].ID_Estudiante
        estudiante = Usuario.query.get(estudiante_id)
        
        print(f"DEBUG: Estudiante seleccionado: {estudiante.Nombre if estudiante else 'None'} (ID: {estudiante_id})")
        print(f"DEBUG: Asignatura seleccionada: {asignatura.Nombre} (ID: {asignatura.ID_Asignatura})")

        # Consultar notas del estudiante para la asignatura seleccionada, ordenadas por período
        registros = Nota_Calificaciones.query.filter_by(
            ID_Estudiante=estudiante_id,
            ID_Asignatura=asignatura.ID_Asignatura
        ).order_by(Nota_Calificaciones.Periodo.asc()).all()
        
        print(f"DEBUG: Registros de notas encontrados: {len(registros)}")
        
        # Si no hay registros, simplemente mostrar la tabla vacía
        if len(registros) == 0:
            print("DEBUG: No hay registros de notas para este estudiante en esta asignatura")
            print("DEBUG: Verificando si existen notas para este estudiante en otras asignaturas...")
            todas_notas_estudiante = Nota_Calificaciones.query.filter_by(
                ID_Estudiante=estudiante_id
            ).all()
            print(f"DEBUG: Total de notas del estudiante {estudiante_id}: {len(todas_notas_estudiante)}")
            for nota in todas_notas_estudiante:
                asignatura_nota = Asignatura.query.get(nota.ID_Asignatura)
                print(f"  - Asignatura: {asignatura_nota.Nombre if asignatura_nota else 'Unknown'} (ID: {nota.ID_Asignatura}), Período: {nota.Periodo}")
        
        # Verificar si existen notas para esta asignatura en otros estudiantes
        print(f"DEBUG: Verificando si existen notas para la asignatura {asignatura.Nombre} en otros estudiantes...")
        todas_notas_asignatura = Nota_Calificaciones.query.filter_by(
            ID_Asignatura=asignatura.ID_Asignatura
        ).all()
        print(f"DEBUG: Total de notas para la asignatura {asignatura.ID_Asignatura}: {len(todas_notas_asignatura)}")
        for nota in todas_notas_asignatura:
            print(f"  - Estudiante ID: {nota.ID_Estudiante}, Período: {nota.Periodo}")
        
        for r in registros:
            print(f"  - Período: {r.Periodo}, Notas: {r.Nota_1}/{r.Nota_2}/{r.Nota_3}/{r.Nota_4}/{r.Nota_5}, Promedio: {r.Promedio_Final}")

    # Calcular promedio general (solo promedios no nulos)
    promedios_validos = [r.Promedio_Final for r in registros if getattr(r, 'Promedio_Final', None) is not None]
    promedio_general = round(sum(promedios_validos) / len(promedios_validos), 2) if promedios_validos else None
    
    print(f"DEBUG: Promedio general calculado: {promedio_general}")

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
@login_required
def inasistencias_justificadas():
    print("[DEBUG inasistencias_justificadas] ID_Usuario actual=", current_user.ID_Usuario)

    # Buscar estudiantes asociados al acudiente actual
    relaciones = Acudiente.query.filter_by(ID_Usuario=current_user.ID_Usuario, Estado='Activo').all()
    print("[DEBUG inasistencias_justificadas] relaciones encontradas=", len(relaciones))

    if not relaciones:
        flash("No tiene estudiantes asociados.", "warning")
        return render_template('Acudiente/InasistenciasJustificadas.html', faltas=[])

    estudiante_id = relaciones[0].ID_Estudiante
    print("[DEBUG inasistencias_justificadas] usando ID_Estudiante=", estudiante_id)

    # Faltas del estudiante marcadas como Ausente y sin excusa registrada aún
    faltas = Detalle_Asistencia.query.filter(
        Detalle_Asistencia.ID_Estudiante == estudiante_id,
        Detalle_Asistencia.Estado_Asistencia == 'Ausente',
        Detalle_Asistencia.TextoExcusa.is_(None)
    ).order_by(Detalle_Asistencia.ID_Detalle_Asistencia.desc()).all()

    print("[DEBUG inasistencias_justificadas] faltas encontradas=", len(faltas))

    return render_template('Acudiente/InasistenciasJustificadas.html', faltas=faltas)

@Acudiente_bp.route('/informes_academicos')
def informes_academicos():
    return render_template('Acudiente/InformesAcademicos.html')

@Acudiente_bp.route('/comunicados')
def comunicados():
    return render_template('Acudiente/Comunicados.html')

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