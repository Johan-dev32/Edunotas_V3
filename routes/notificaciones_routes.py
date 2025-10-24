# notificaciones_routes.py
from flask import Blueprint, request, jsonify
from Controladores.models import db, Usuario, Notificacion
from flask_login import current_user, login_required

notificaciones_bp = Blueprint('notificaciones_bp', __name__, url_prefix='/notificaciones')

# 📨 Enviar notificación general (a todos los roles)
@notificaciones_bp.route('/notificaciones/enviar_todos', methods=['POST'])
@login_required
def enviar_a_todos():
    data = request.get_json()
    titulo = data.get('titulo')
    contenido = data.get('contenido')

    if current_user.rol != "Administrador":
        return jsonify({"error": "Solo el administrador puede enviar notificaciones generales"}), 403

    usuarios = Usuario.query.filter(Usuario.rol.in_(["Docente", "Estudiante", "Acudiente"])).all()

    for u in usuarios:
        notificacion = Notificacion(usuario_id=u.id, titulo=titulo, contenido=contenido)
        db.session.add(notificacion)

    db.session.commit()
    return jsonify({"mensaje": "Notificación enviada a todos los roles"}), 200


# 📩 Enviar notificación individual
@notificaciones_bp.route('/notificaciones/enviar', methods=['POST'])
@login_required
def enviar_individual():
    data = request.get_json()
    destinatario_id = data.get('destinatario_id')
    titulo = data.get('titulo')
    contenido = data.get('contenido')

    notificacion = Notificacion(usuario_id=destinatario_id, titulo=titulo, contenido=contenido)
    db.session.add(notificacion)
    db.session.commit()

    return jsonify({"mensaje": "Notificación enviada correctamente"}), 200


# 🔔 Consultar notificaciones del usuario logueado
@notificaciones_bp.route('/notificaciones/mis_notificaciones', methods=['GET'])
@login_required
def mis_notificaciones():
    notificaciones = Notificacion.query.filter_by(usuario_id=current_user.id).order_by(Notificacion.fecha.desc()).all()
    lista = [
        {"titulo": n.titulo, "contenido": n.contenido, "fecha": n.fecha.strftime("%d/%m/%Y %H:%M")}
        for n in notificaciones
    ]
    return jsonify(lista)