import os
import re
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file, jsonify  # <-- añadí send_file, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from routes.Administrador import Administrador_bp
from routes.Docente import Docente_bp
from routes.Acudiente import Acudiente_bp
from routes.Estudiante import Estudiante_bp
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired,BadSignature

mail = Mail()

s = URLSafeTimedSerializer("clave_super_secreta")

import pymysql

# Importa el objeto 'db' y los modelos desde tu archivo de modelos
from Controladores.models import db, Usuario, Acudiente, Curso, Matricula, Periodo, Asignatura, Docente_Asignatura, Programacion, Asistencia, Detalle_Asistencia, Cronograma_Actividades, Actividad, Actividad_Estudiante, Observacion

# Configuración de la aplicación
app = Flask(__name__)

# Configuración de la base de datos
DB_URL = 'mysql+pymysql://root:@127.0.0.1:3306/edunotas'
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'clave_super_secreta'
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_pre_ping': True}

app.config.update(
    MAIL_SERVER="smtp.gmail.com",
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USE_SSL=False,
    MAIL_USERNAME=os.getenv("MAIL_USERNAME", "soniagisell67@gmail.com"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD", "tadvqwwnkzajmwvm"),
    MAIL_DEFAULT_SENDER=(
        "Edunotas",
        os.getenv("MAIL_USERNAME", "soniagisell67@gmail.com"),
    ),
)
mail.init_app(app)


# Inicializa la instancia de SQLAlchemy con la aplicación
db.init_app(app)

# Inicialización de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Esta función es requerida por Flask-Login para cargar un usuario
@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# Crea la base de datos y las tablas si no existen
with app.app_context():
    engine = create_engine(DB_URL)
    if not database_exists(engine.url):
        create_database(engine.url)
        print("Base de datos 'edunotas' creada exitosamente.")
    db.create_all()
    print("Tablas de la base de datos creadas exitosamente.")
    
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

# ---------------- RUTAS PRINCIPALES ----------------

@app.route('/')
def index():
    return render_template("Login.html")

@app.route('/indexadministrador')
@login_required
def indexadministrador():
    return render_template("Administrador/Paginainicio_Administrador.html", usuario=current_user)

@app.route('/indexestudiante')
@login_required
def indexestudiante():
    return render_template("Estudiante/Paginainicio_Estudiante.html", usuario=current_user)

@app.route('/indexdocente')
@login_required
def indexdocente():
    return render_template("Docentes/Paginainicio_Docentes.html", usuario=current_user)

@app.route('/indexacudiente')
@login_required
def indexacudiente():
    return render_template("Acudiente/Paginainicio_Acudiente.html", usuario=current_user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
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

        
        rol_usuario = usuario.Rol  

        if rol_usuario != rol:
            flash("El rol seleccionado no coincide con el asignado al usuario.")
            return redirect(url_for('login'))

        
        login_user(usuario)
        flash('Inicio de sesión exitoso')

        
        rol = usuario.Rol

        if rol == 'Administrador':
            return redirect(url_for('indexadministrador'))
        elif rol == 'Docente':
            return redirect(url_for('indexdocente'))
        elif rol == 'Estudiante':
            return redirect(url_for('indexestudiante'))
        elif rol == 'Acudiente':
            return redirect(url_for('indexacudiente'))
        else:
            flash("Rol no reconocido en el sistema.")
            return redirect(url_for('login'))

    return render_template('login.html')

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
        
@app.route('/manual')
def manual():
    return render_template('manual.html')


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
        user.Contraseña = generate_password_hash(new_password)
        db.session.commit()

        flash('Contraseña restablecida correctamente.', 'success')
        return redirect(url_for('login'))

    return render_template('reset_password.html', token=token)


app.register_blueprint(Administrador_bp)
app.register_blueprint(Docente_bp)
app.register_blueprint(Estudiante_bp)
app.register_blueprint(Acudiente_bp)


if __name__ == "__main__":
    app.run(debug=True)
