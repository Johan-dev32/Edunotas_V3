# notificaciones_routes.py
from flask import Blueprint, request, jsonify, session
from Controladores.models import db, Usuario, Notificacion
from flask_login import current_user, login_required

notificaciones_bp = Blueprint('notificaciones_bp', __name__, url_prefix='/notificaciones')

@notificaciones_bp.route('/notificaciones/recibir')
def recibir_notificaciones():
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({"error": "Usuario no autenticado"}), 401

        mensajes = Notificacion.query.filter_by(ID_Usuario=user_id, Estado='No leída').all()

        lista = [{"titulo": msg.Titulo, "mensaje": msg.Mensaje, "enlace": msg.Enlace} for msg in mensajes]

        return jsonify(lista)
    except Exception as e:
        return jsonify({"error": str(e)}), 500