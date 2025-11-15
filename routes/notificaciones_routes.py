# notificaciones_routes.py
from flask import Blueprint, request, jsonify, session
from Controladores.models import db, Usuario, Notificacion
from flask_login import current_user, login_required

notificaciones_bp = Blueprint('notificaciones_bp', __name__, url_prefix='/notificaciones')

# GET /notificaciones/recibir
@notificaciones_bp.route('/recibir', methods=['GET'])
@login_required
def recibir_notificaciones():
    try:
        # Preferir el usuario autenticado de Flask-Login; usar sesión solo como respaldo
        user_id = getattr(current_user, 'ID_Usuario', None) or session.get('user_id')
        if not user_id:
            return jsonify([]), 200

        mensajes = (
            Notificacion.query
            .filter_by(ID_Usuario=user_id)
            .order_by(Notificacion.Fecha.desc())
            .limit(10)
            .all()
        )

        try:
            print(f"[notificaciones.recibir] user_id={user_id}, count={len(mensajes)}")
        except Exception:
            pass
        lista = [{"titulo": msg.Titulo, "contenido": msg.Mensaje, "enlace": msg.Enlace} for msg in mensajes]
        return jsonify(lista)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# POST /notificaciones/enviar_todos
@notificaciones_bp.route('/enviar_todos', methods=['POST'])
@login_required
def enviar_todos():
    try:
        data = request.get_json(silent=True) or {}
        titulo = (data.get('titulo') or '').strip()
        contenido = (data.get('contenido') or '').strip()
        rol = (data.get('rol') or 'Todos').strip()

        if not titulo or not contenido:
            return jsonify({"error": "Título y contenido son obligatorios"}), 400

        q = Usuario.query
        roles_validos = {"Administrador", "Docente", "Estudiante", "Acudiente"}
        if rol != 'Todos':
            if rol not in roles_validos:
                return jsonify({"error": "Rol no válido"}), 400
            q = q.filter(Usuario.Rol == rol)

        destinatarios = q.filter(Usuario.Estado == 'Activo').all()
        if not destinatarios:
            return jsonify({"ok": True, "enviados": 0})

        nuevas = [
            Notificacion(Titulo=titulo, Mensaje=contenido, Enlace=None, ID_Usuario=u.ID_Usuario)
            for u in destinatarios
        ]
        db.session.bulk_save_objects(nuevas)
        db.session.commit()
        return jsonify({"ok": True, "enviados": len(nuevas)})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# GET /notificaciones/contador
@notificaciones_bp.route('/contador', methods=['GET'])
@login_required
def contador_notificaciones():
    try:
        user_id = getattr(current_user, 'ID_Usuario', None) or session.get('user_id')
        if not user_id:
            return jsonify({"unread": 0})

        unread = (
            db.session.query(Notificacion)
            .filter_by(ID_Usuario=user_id, Estado='No leída')
            .count()
        )
        return jsonify({"unread": unread})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# POST /notificaciones/marcar_leidas
@notificaciones_bp.route('/marcar_leidas', methods=['POST'])
@login_required
def marcar_leidas():
    try:
        user_id = getattr(current_user, 'ID_Usuario', None) or session.get('user_id')
        if not user_id:
            return jsonify({"ok": True, "marcadas": 0})

        marcadas = (
            Notificacion.query
            .filter_by(ID_Usuario=user_id, Estado='No leída')
            .update({Notificacion.Estado: 'Leída'})
        )
        db.session.commit()
        return jsonify({"ok": True, "marcadas": marcadas or 0})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500