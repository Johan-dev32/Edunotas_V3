from app import app, db
from Controladores.models import Usuario, Curso, Asignatura, Periodo

with app.app_context():
    db.create_all()
    print("Tablas creadas exitosamente")
