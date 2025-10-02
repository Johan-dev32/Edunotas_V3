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

# ---------------- RUTAS PRINCIPALES ----------------

@app.route('/')
def index():
    return render_template("Login.html")

@app.route('/indexadministrador')
def indexadministrador():
    return render_template("Administrador/Paginainicio_Administrador.html")

@app.route('/indexestudiante')
def indexestudiante():
    return render_template("Estudiante/Paginainicio_Estudiante.html")

@app.route('/indexdocente')
def indexdocente():
    return render_template("Docentes/Paginainicio_Docentes.html")

@app.route('/indexacudiente')
def indexacudiente():
    return render_template("Acudiente/Paginainicio_Acudiente.html")


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


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión.')
    return redirect(url_for('index'))


app.register_blueprint(Administrador_bp)
app.register_blueprint(Docente_bp)
app.register_blueprint(Estudiante_bp)
app.register_blueprint(Acudiente_bp)


if __name__ == "__main__":
    app.run(debug=True)
