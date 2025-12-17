import os
import re
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from routes.Administrador import Administrador_bp
from routes.Docente import Docente_bp
from routes.Acudiente import Acudiente_bp
from routes.Estudiante import Estudiante_bp
from routes.notificaciones_routes import notificaciones_bp
from flask_mail import Mail, Message
from Controladores.models import db
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature

# Cargar variables de entorno
load_dotenv()


# Inicialización de Flask-Mail
mail = Mail()

# Configuración del serializador con la clave secreta de las variables de entorno
s = URLSafeTimedSerializer(os.getenv('SECRET_KEY', 'clave_por_defecto_segura'))

# Importa el objeto 'db' y los modelos desde tu archivo de modelos
from Controladores.models import db, Usuario, Notificacion

# Configuración de la aplicación
app = Flask(__name__)


# Carpeta donde se guardarán los archivos subidos
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')

# Crear la carpeta si no existe
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Configuración de la base de datos
DB_URL = os.getenv('DATABASE_URL', 'sqlite:///edunotas.db')
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'clave_por_defecto_segura')
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_pre_ping': True}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Configuración de correo electrónico
app.config.update(
    MAIL_SERVER="smtp.gmail.com",
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USE_SSL=False,
    MAIL_USERNAME=os.getenv('MAIL_USERNAME'),
    MAIL_PASSWORD=os.getenv('MAIL_PASSWORD'),
    MAIL_DEFAULT_SENDER=(
        "Edunotas",
        os.getenv("MAIL_USERNAME", "edunotas2025@gmail.com"),
    ),
)
mail.init_app(app)


# Inicializa la instancia de SQLAlchemy con la aplicación
db.init_app(app)

# habilita WebSocket


# Inicialización de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Agregar filtro personalizado para formatear números
@app.template_filter('format_number')
def format_number(value):
    """Formatea un número para mostrar siempre un decimal"""
    if value is None:
        return ''
    
    try:
        # Convertir a float
        num = float(value)
        
        # Siempre mostrar con un decimal
        return f"{num:.1f}"
    except (ValueError, TypeError):
        return str(value)

# Esta función es requerida por Flask-Login para cargar un usuario
@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# Crea las tablas si no existen
with app.app_context():
    try:
        db.create_all()
        print("Tablas de la base de datos verificadas/creadas exitosamente.")
        
        # Crear usuario administrador por defecto si no existe
        admin_exists = Usuario.query.filter_by(Rol='Administrador').first()
        if not admin_exists:
            admin = Usuario(
                Nombre='Juan',
                Apellido='Rivera',
                Correo='juancamiloriveraduquino77@gmail.com',
                Contrasena=generate_password_hash('123456789'),
                Rol='Administrador',
                Genero='M',
                Direccion='',
                Telefono=''
            )
            db.session.add(admin)
            db.session.commit()
            print("Administrador creado exitosamente")
    except Exception as e:
        print(f"Error al inicializar la base de datos: {str(e)}")
        print("Continuando con la aplicación...")
    
###nuevo    
def send_reset_email(user_email, user_name, token):
    reset_url = url_for('reset_password', token=token, _external=True)
    msg = Message(
        subject="Recuperación de contraseña - Edunotas",
        recipients=[user_email]
    )
    msg.html = render_template(
        'email_reset.html',
        user_name=user_name,
        reset_url=reset_url
    )
    mail.send(msg)  

def validar_password(password):
    """Valida que la contraseña cumpla con las políticas de seguridad."""
    if len(password) < 8:
        return "La contraseña debe tener al menos 8 caracteres."
    if not re.search(r"[A-Z]", password):
        return "La contraseña debe contener al menos una letra mayúscula."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return "La contraseña debe contener al menos un carácter especial."
    if re.search(r"(012|123|234|345|456|567|678|789)", password):
        return "La contraseña no puede contener números consecutivos."
    return None

@app.errorhandler(500)
def internal_server_error(e):
    print(f"Error 500: {str(e)}")
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Error</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
            .error-box { max-width: 500px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }
            .btn { background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 3px; display: inline-block; margin-top: 20px; }
        </style>
    </head>
    <body>
        <div class="error-box">
            <h2>Ocurrió un error inesperado</h2>
            <p>Por favor, inténtalo de nuevo más tarde.</p>
            <a href="/login" class="btn">Volver al login</a>
        </div>
    </body>
    </html>
    """, 500

@app.errorhandler(Exception)
def handle_exception(e):
    print(f"Excepción no manejada: {str(e)}")
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Error</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
            .error-box { max-width: 500px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }
            .btn { background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 3px; display: inline-block; margin-top: 20px; }
        </style>
    </head>
    <body>
        <div class="error-box">
            <h2>Ocurrió un error inesperado</h2>
            <p>Por favor, inténtalo de nuevo más tarde.</p>
            <a href="/login" class="btn">Volver al login</a>
        </div>
    </body>
    </html>
    """, 500

# ---------------- RUTAS PRINCIPALES ----------------

@app.route('/')
def index():
    return render_template("Login.html")

@app.route('/indexadministrador')
@login_required
def indexadministrador():
    # Obtener el primer nombre y primer apellido del usuario
    if current_user and current_user.is_authenticated:
        print(f"Usuario autenticado en indexadministrador: {current_user}")
        print(f"Nombre: {current_user.Nombre}")
        print(f"Apellido: {current_user.Apellido}")
        
        nombre_completo = current_user.Nombre.split() if current_user.Nombre else []
        apellido_completo = current_user.Apellido.split() if current_user.Apellido else []
        
        primer_nombre = nombre_completo[0] if nombre_completo else ""
        primer_apellido = apellido_completo[0] if apellido_completo else ""
        
        nombre_usuario = f"{primer_nombre} {primer_apellido}"
        print(f"Nombre usuario generado en indexadministrador: {nombre_usuario}")
    else:
        nombre_usuario = ""
        print("Usuario no autenticado en indexadministrador")
    
    return render_template("Administrador/Paginainicio_Administrador.html", nombre_usuario=nombre_usuario)

@app.route('/indexestudiante')
@login_required
def indexestudiante():
    return render_template("Estudiante/Paginainicio_Estudiante.html", usuario=current_user)

@app.route('/indexdocente')
@login_required
def indexdocente():
    if current_user.is_authenticated:
        nombre_completo = current_user.Nombre.split() if current_user.Nombre else []
        apellido_completo = current_user.Apellido.split() if current_user.Apellido else []
        
        primer_nombre = nombre_completo[0] if nombre_completo else ""
        primer_apellido = apellido_completo[0] if apellido_completo else ""
        
        nombre_usuario = f"{primer_nombre} {primer_apellido}"
        print(f"Nombre usuario generado en indexdocente: {nombre_usuario}")
    else:
        nombre_usuario = ""
        print("Usuario no autenticado en indexdocente")
    
    return render_template("Docentes/Paginainicio_Docentes.html", usuario=current_user, nombre_usuario=nombre_usuario)

@app.route('/indexacudiente')
@login_required
def indexacudiente():
    if current_user.is_authenticated:
        nombre_usuario = current_user.Nombre
        print(f"Nombre usuario generado en indexacudiente: {nombre_usuario}")
    else:
        nombre_usuario = ""
        print("Usuario no autenticado en indexacudiente")
    
    return render_template("Acudiente/Paginainicio_Acudiente.html", usuario=current_user, nombre_usuario=nombre_usuario)



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            correo = request.form.get('email')
            contrasena = request.form.get('password')
            rol = request.form.get('rol')
            
            usuario = Usuario.query.filter_by(Correo=correo).first()

            if not usuario:
                flash("Correo incorrecto.")
                return redirect(url_for('login'))

            if not check_password_hash(usuario.Contrasena, contrasena):
                flash("Contraseña incorrecta.")
                return redirect(url_for('login'))

            if usuario.Rol != rol:
                flash("El rol seleccionado no coincide con el asignado al usuario.")
                return redirect(url_for('login'))

            login_user(usuario)
            flash('Inicio de sesión exitoso')
            
            session['nombre_usuario'] = usuario.Nombre
            session['genero_usuario'] = usuario.Genero


            if rol == 'Administrador':
                return redirect(url_for('loading', destino='indexadministrador'))
            elif rol == 'Docente':
                return redirect(url_for('loading', destino='indexdocente'))
            elif rol == 'Estudiante':
                return redirect(url_for('loading', destino='indexestudiante'))
            elif rol == 'Acudiente':
                return redirect(url_for('loading', destino='indexacudiente'))
            else:
                flash("Rol no reconocido en el sistema.")
                return redirect(url_for('login'))
        except Exception as e:
            print(f"Error en login: {str(e)}")
            flash("Ocurrió un error al intentar iniciar sesión. Por favor, inténtalo de nuevo.")
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/loading/<destino>')
def loading(destino):
    return render_template('loading.html', destino=destino)

@app.route("/perfil")
@login_required
def perfil():
    return render_template("perfil.html", usuario=current_user)

@app.route('/perfil/<rol>')
def perfil_rol(rol):
        if rol == "Administrador":
            return render_template("inicio_admin.html")
        elif rol == "Docente":
            return render_template("inicio_docente.html")
        elif rol == "Estudiante":
            return render_template("inicio_estudiante.html")
        elif rol == "Acudiente":
            return render_template("inicio_acudiente.html")
        else:
            return "Rol no válido", 404

        
@app.route('/actualizar_perfil', methods=['POST'])
@login_required
def actualizar_perfil():
    try:
        usuario = Usuario.query.get(current_user.ID_Usuario)

        # Datos del formulario
        nombre = request.form.get('nombre')
        apellido = request.form.get('apellido')
        correo = request.form.get('correo')
        direccion = request.form.get('direccion')
        telefono = request.form.get('telefono')

        # Tomar snapshot previo para comparar cambios
        prev = {
            'Nombre': usuario.Nombre,
            'Apellido': usuario.Apellido,
            'Correo': usuario.Correo,
            'Direccion': usuario.Direccion,
            'Telefono': usuario.Telefono,
        }

        # Verificar si el nuevo correo pertenece a otro usuario
        correo_existente = Usuario.query.filter(
            Usuario.Correo == correo,
            Usuario.ID_Usuario != usuario.ID_Usuario
        ).first()

        if correo_existente:
            return jsonify({
                'status': 'error',
                'message': 'El correo ya está registrado por otro usuario.'
            })

        # Actualizar solo si hay cambios
        usuario.Nombre = nombre
        usuario.Apellido = apellido
        usuario.Correo = correo
        usuario.Direccion = direccion
        usuario.Telefono = telefono

        db.session.commit()

        # Construir resumen de cambios y generar notificación + correo
        cambios = []
        if prev['Nombre'] != nombre or prev['Apellido'] != apellido:
            cambios.append(f"Nombre completo: {prev['Nombre']} {prev['Apellido']} → {nombre} {apellido}")
        if prev['Correo'] != correo:
            cambios.append(f"Correo electrónico: {prev['Correo']} → {correo}")
        if (prev['Direccion'] or '') != (direccion or ''):
            cambios.append("Dirección de residencia actualizada")
        if (prev['Telefono'] or '') != (telefono or ''):
            cambios.append(f"Teléfono: {prev['Telefono'] or '—'} → {telefono or '—'}")

        if cambios:
            try:
                resumen = "; ".join(cambios)
                # Guardar notificación en el sistema
                noti = Notificacion(
                    Titulo='Actualización de perfil',
                    Mensaje=f"Se actualizaron estos datos de tu perfil: {resumen}.",
                    Enlace=None,
                    ID_Usuario=usuario.ID_Usuario
                )
                db.session.add(noti)
                db.session.commit()

                # Enviar correo al usuario afectado
                try:
                    msg = Message(
                        subject='Edunotas - Actualización de perfil',
                        recipients=[usuario.Correo]
                    )
                    msg.html = render_template(
                        'email_generico.html',
                        titulo='Actualización de perfil',
                        cuerpo=f"Hola {usuario.Nombre},<br><br>Hemos detectado cambios en tu perfil:<br>• " + "<br>• ".join(cambios) + "<br><br>Si no fuiste tú, por favor comunícate con el administrador."
                    )
                    mail.send(msg)
                except Exception as _:
                    # Evitar romper el flujo si falla el correo
                    pass
            except Exception as _:
                db.session.rollback()

        return jsonify({
            'status': 'success',
            'message': 'Datos actualizados correctamente.'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Ocurrió un error: {str(e)}'
        })


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión.')
    return redirect(url_for('index'))


# ------------------ FORGOT_PASSWORD ------------------ #
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get("email")
        user = Usuario.query.filter_by(Correo=email).first()
        if user:
            try:
                token = s.dumps(email, salt='password-recovery')
                send_reset_email(user_email=email, user_name=user.Nombre, token=token)
                flash('Correo enviado.', 'success')
            except Exception as e:
                flash(f'Error: {e}', 'danger')
        else:
            flash('Correo no registrado.', 'warning')
    return render_template("forgot_password.html")


# ------------------ RESET_PASSWORD ------------------ #
@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        email = s.loads(token, salt='password-recovery', max_age=3600)
    except (SignatureExpired, BadSignature):
        flash('Enlace inválido o expirado.', 'danger')
        return redirect(url_for('forgot_password'))

    if request.method == 'POST':
        new_password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Validación: campos completos
        if not new_password or not confirm_password:
            flash('Completa ambos campos.', 'warning')
            return render_template('reset_password.html', token=token)

        # Validación: contraseñas coinciden
        if new_password != confirm_password:
            flash('Las contraseñas no coinciden.', 'warning')
            return render_template('reset_password.html', token=token)

        # Validación de política de seguridad
        error = validar_password(new_password)
        if error:
            flash(error, 'warning')
            return render_template('reset_password.html', token=token)

        # Buscar usuario
        user = Usuario.query.filter_by(Correo=email).first()
        if not user:
            flash('Usuario no encontrado.', 'danger')
            return redirect(url_for('forgot_password'))

        # Actualizar contraseña
        user.Contrasena = generate_password_hash(new_password)
        db.session.commit()

        flash('Contraseña restablecida correctamente.', 'success')
        return redirect(url_for('login'))

    return render_template('reset_password.html', token=token)



app.register_blueprint(Administrador_bp)
app.register_blueprint(Docente_bp)
app.register_blueprint(Estudiante_bp)
app.register_blueprint(Acudiente_bp)
app.register_blueprint(notificaciones_bp)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
    

