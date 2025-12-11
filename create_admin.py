from app import app, db
from Controladores.models import Usuario
from werkzeug.security import generate_password_hash

with app.app_context():
    # Verificar si ya existe un administrador
    admin_exists = Usuario.query.filter_by(Rol='Administrador').first()
    
    if not admin_exists:
        # Crear usuario administrador por defecto
        admin = Usuario(
            Nombre='Juan',
            Apellido='Rivera',
            Correo='juancamiloriveraduquino77@gmail.com',
            Contrasena=generate_password_hash('123456789'),
            Rol='Administrador',
            Genero='Masculino',
            Direccion='',
            Telefono=''
        )
        
        db.session.add(admin)
        db.session.commit()
        print("Administrador creado exitosamente")
    else:
        print("El administrador ya existe")
