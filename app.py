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

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form.get('Nombre')
        apellido = request.form.get('Apellido')
        correo = request.form.get('Correo')
        contrasena = request.form.get('Contrasena')
        numero_documento = request.form.get('NumeroDocumento')
        telefono = request.form.get('Telefono')
        direccion = request.form.get('Direccion')
        rol = request.form.get('Rol')

        tipo_documento = request.form.get('TipoDocumento', 'CC')
        estado = request.form.get('Estado', 'Activo')
        genero = request.form.get('Genero', '')

        if not all([nombre, apellido, correo, contrasena, numero_documento, telefono, direccion, rol]):
            flash('Por favor, completa todos los campos requeridos.')
            return render_template('Administrador/templates/Registro.html')

        try:
            existing_user = Usuario.query.filter_by(Correo=correo).first()
            if existing_user:
                flash('El correo ya está registrado.')
                return render_template('Administrador/templates/Registro.html')

            hashed_password = generate_password_hash(contrasena)
            
            new_user = Usuario(
                Nombre=nombre,
                Apellido=apellido,
                Correo=correo,
                Contrasena=hashed_password,
                TipoDocumento=tipo_documento,
                NumeroDocumento=numero_documento,
                Telefono=telefono,
                Direccion=direccion,
                Rol=rol,
                Estado=estado,
                Genero=genero
            )
            
            
            db.session.add(new_user)
            db.session.commit()

            flash('Cuenta creada exitosamente. Inicia sesión.')
            return redirect(url_for('login'))
        
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Error al registrar: {str(e)}')
            return render_template('Administrador/templates/Registro.html')

    return render_template('Administrador/templates/Registro.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form['email']
        contrasena = request.form['password']
        
        usuario = Usuario.query.filter_by(Correo=correo).first()

        if usuario and check_password_hash(usuario.Contrasena, contrasena):
            login_user(usuario)

            # Redirigir según rol
            if usuario.Rol == 'Administrador':
                return redirect(url_for('Administrador.paginainicio'))
            elif usuario.Rol == 'Docente':
                return redirect(url_for('Docente.paginainicio'))
            elif usuario.Rol == 'Estudiante':
                return redirect(url_for('Estudiante.paginainicio'))
            elif usuario.Rol == 'Acudiente':
                return redirect(url_for('Acudiente.paginainicio'))
        else:
            flash("Correo o contraseña incorrectos", "danger")

    return render_template('Login.html')




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
