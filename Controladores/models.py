# models.py
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Date, Enum, Text, ForeignKey, Time
from sqlalchemy import Numeric as DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import YEAR
from flask_login import UserMixin

db = SQLAlchemy()

# -----------------------------------------------------
# Usuario
# -----------------------------------------------------
class Usuario(db.Model, UserMixin):
    __tablename__ = 'Usuario'
    ID_Usuario = db.Column(Integer, primary_key=True, autoincrement=True)
    Nombre = db.Column(String(100), nullable=False)
    Apellido = db.Column(String(100), nullable=False)
    Correo = db.Column(String(150), unique=True, nullable=False)
    Contrasena = db.Column(String(255), nullable=False)
    TipoDocumento = db.Column(String(50))
    NumeroDocumento = db.Column(String(50), unique=True)
    Direccion = db.Column(String(200))
    Telefono = db.Column(String(50))
    Estado = db.Column(Enum('Activo', 'Inactivo'), default='Activo')
    Genero = db.Column(Enum('M', 'F', 'Otro'))
    Rol = db.Column(Enum('Administrador', 'Docente', 'Estudiante', 'Acudiente'), nullable=False)

    # Relaciones
    matriculas = relationship('Matricula', back_populates='estudiante', lazy='dynamic', foreign_keys='Matricula.ID_Estudiante')
    acudientes = relationship('Acudiente', back_populates='usuario', lazy='dynamic', foreign_keys='Acudiente.ID_Usuario')
    docente_asignaturas = relationship('Docente_Asignatura', back_populates='docente', lazy='dynamic', foreign_keys='Docente_Asignatura.ID_Docente')
    asistencias_detalle = relationship('Detalle_Asistencia', back_populates='estudiante', lazy='dynamic', foreign_keys='Detalle_Asistencia.ID_Estudiante')
    cursos_dirige = relationship('Curso', back_populates='director', lazy='dynamic', foreign_keys='Curso.DirectorGrupo')

    def get_id(self):
        return str(self.ID_Usuario)


# -----------------------------------------------------
# Acudiente
# -----------------------------------------------------
class Acudiente(db.Model):
    __tablename__ = 'Acudiente'
    ID_Acudiente = db.Column(Integer, primary_key=True, autoincrement=True)
    ID_Usuario = db.Column(Integer, ForeignKey('Usuario.ID_Usuario'), nullable=False)  # acudiente
    ID_Estudiante = db.Column(Integer, ForeignKey('Usuario.ID_Usuario'), nullable=False)  # estudiante
    Parentesco = db.Column(Enum('Padre', 'Madre', 'Abuelo', 'Abuela', 'Tio', 'Tia', 'Primo', 'Prima'))
    Estado = db.Column(Enum('Activo', 'Inactivo'), default='Activo')

    # Relaciones
    usuario = relationship('Usuario', back_populates='acudientes', foreign_keys=[ID_Usuario])



# -----------------------------------------------------
# Notificaciòn(nuevo)
# -----------------------------------------------------
class Notificacion(db.Model):
    __tablename__ = "Notificacion"
    ID_Notificacion = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Titulo = db.Column(db.String(150), nullable=False)
    Mensaje = db.Column(db.String(300), nullable=False)
    Enlace = db.Column(db.String(255), nullable=True)
    Estado = db.Column(db.Enum('Leída', 'No leída'), default='No leída')
    Fecha = db.Column(db.DateTime, default=db.func.now())

    # Relación con usuario
    ID_Usuario = db.Column(db.Integer, db.ForeignKey("Usuario.ID_Usuario"), nullable=False)
    usuario = db.relationship("Usuario", backref="notificaciones", lazy=True)



# -----------------------------------------------------
# Curso
# -----------------------------------------------------
class Curso(db.Model):
    __tablename__ = 'Curso'
    ID_Curso = db.Column(Integer, primary_key=True, autoincrement=True)
    Grado = db.Column(String(10), nullable=False)
    Grupo = db.Column(String(10))
    Anio = db.Column(YEAR, nullable=False)
    Estado = db.Column(Enum('Activo', 'Inactivo'), default='Activo')
    DirectorGrupo = db.Column(Integer, ForeignKey('Usuario.ID_Usuario'))

    # Relaciones
    director = relationship('Usuario', back_populates='cursos_dirige', foreign_keys=[DirectorGrupo])
    matriculas = relationship('Matricula', back_populates='curso', lazy='dynamic')
    cronogramas = relationship('Cronograma_Actividades', back_populates='curso', lazy='dynamic')
    programaciones = relationship('Programacion', back_populates='curso', lazy='dynamic')


# -----------------------------------------------------
# Matricula
# -----------------------------------------------------
class Matricula(db.Model):
    __tablename__ = 'Matricula'
    ID_Matricula = db.Column(Integer, primary_key=True, autoincrement=True)
    ID_Estudiante = db.Column(Integer, ForeignKey('Usuario.ID_Usuario'), nullable=False)
    ID_Curso = db.Column(Integer, ForeignKey('Curso.ID_Curso'), nullable=False)
    AnioLectivo = db.Column(YEAR, nullable=False)

    # Relaciones
    estudiante = relationship('Usuario', back_populates='matriculas', foreign_keys=[ID_Estudiante])
    curso = relationship('Curso', back_populates='matriculas', foreign_keys=[ID_Curso])
    observaciones = relationship('Observacion', back_populates='matricula', lazy='dynamic')
    actividades_estudiante = relationship('Actividad_Estudiante', back_populates='matricula', lazy='dynamic')


# -----------------------------------------------------
# Periodo
# -----------------------------------------------------
class Periodo(db.Model):
    __tablename__ = 'Periodo'
    ID_Periodo = db.Column(Integer, primary_key=True, autoincrement=True)
    NumeroPeriodo = db.Column(Integer, nullable=False)
    Anio = db.Column(YEAR, nullable=False)
    FechaInicial = db.Column(Date)
    FechaFinal = db.Column(Date)

    # Relaciones
    cronogramas = relationship('Cronograma_Actividades', back_populates='periodo', lazy='dynamic')


# -----------------------------------------------------
# Asignatura
# -----------------------------------------------------
class Asignatura(db.Model):
    __tablename__ = 'Asignatura'
    ID_Asignatura = db.Column(Integer, primary_key=True, autoincrement=True)
    Nombre = db.Column(String(100), nullable=False)
    Descripcion = db.Column(Text)
    Grado = db.Column(String(10))
    Area = db.Column(String(100))
    CodigoAsignatura = db.Column(String(20), unique=True)
    Estado = db.Column(Enum('Activa', 'Inactiva'), default='Activa')

    # Relaciones
    docente_asignaturas = relationship('Docente_Asignatura', back_populates='asignatura', lazy='dynamic')


# -----------------------------------------------------
# Docente_Asignatura
# -----------------------------------------------------
class Docente_Asignatura(db.Model):
    __tablename__ = 'Docente_Asignatura'
    ID_Docente_Asignatura = db.Column(Integer, primary_key=True, autoincrement=True)
    ID_Docente = db.Column(Integer, ForeignKey('Usuario.ID_Usuario'), nullable=False)
    ID_Asignatura = db.Column(Integer, ForeignKey('Asignatura.ID_Asignatura'), nullable=False)

    # Relaciones
    docente = relationship('Usuario', back_populates='docente_asignaturas', foreign_keys=[ID_Docente])
    asignatura = relationship('Asignatura', back_populates='docente_asignaturas', foreign_keys=[ID_Asignatura])
    programaciones = relationship('Programacion', back_populates='docente_asignatura', lazy='dynamic')


# -----------------------------------------------------
# Programacion (Horario)
# -----------------------------------------------------
class Programacion(db.Model):
    __tablename__ = 'Programacion'
    ID_Programacion = db.Column(Integer, primary_key=True, autoincrement=True)
    ID_Curso = db.Column(Integer, ForeignKey('Curso.ID_Curso'), nullable=False)
    ID_Docente_Asignatura = db.Column(Integer, ForeignKey('Docente_Asignatura.ID_Docente_Asignatura'), nullable=False)
    HoraInicio = db.Column(Time)
    HoraFin = db.Column(Time)
    Dia = db.Column(String(20))

    # Relaciones
    curso = relationship('Curso', back_populates='programaciones', foreign_keys=[ID_Curso])
    docente_asignatura = relationship('Docente_Asignatura', back_populates='programaciones', foreign_keys=[ID_Docente_Asignatura])
    asistencias = relationship('Asistencia', back_populates='programacion', lazy='dynamic')
    observaciones = relationship('Observacion', back_populates='programacion', lazy='dynamic')


# -----------------------------------------------------
# Asistencia
# -----------------------------------------------------
class Asistencia(db.Model):
    __tablename__ = 'Asistencia'
    ID_Asistencia = db.Column(Integer, primary_key=True, autoincrement=True)
    Fecha = db.Column(Date, nullable=False)
    ID_Programacion = db.Column(Integer, ForeignKey('Programacion.ID_Programacion'), nullable=False)

    # Relaciones
    programacion = relationship('Programacion', back_populates='asistencias', foreign_keys=[ID_Programacion])
    detalles = relationship('Detalle_Asistencia', back_populates='asistencia', lazy='dynamic')


# -----------------------------------------------------
# Detalle_Asistencia
# -----------------------------------------------------
class Detalle_Asistencia(db.Model):
    __tablename__ = 'Detalle_Asistencia'
    ID_Detalle_Asistencia = db.Column(Integer, primary_key=True, autoincrement=True)
    ID_Asistencia = db.Column(Integer, ForeignKey('Asistencia.ID_Asistencia'), nullable=False)
    ID_Estudiante = db.Column(Integer, ForeignKey('Usuario.ID_Usuario'), nullable=False)
    Estado_Asistencia = db.Column(Enum('Presente', 'Ausente', 'Justificado'))
    Observaciones = db.Column(Text)

    # Relaciones
    asistencia = relationship('Asistencia', back_populates='detalles', foreign_keys=[ID_Asistencia])
    estudiante = relationship('Usuario', back_populates='asistencias_detalle', foreign_keys=[ID_Estudiante])


# -----------------------------------------------------
# Cronograma_Actividades
# -----------------------------------------------------
class Cronograma_Actividades(db.Model):
    __tablename__ = 'Cronograma_Actividades'
    ID_Cronograma_Actividades = db.Column(Integer, primary_key=True, autoincrement=True)
    ID_Curso = db.Column(Integer, ForeignKey('Curso.ID_Curso'), nullable=False)
    ID_Periodo = db.Column(Integer, ForeignKey('Periodo.ID_Periodo'), nullable=False)
    FechaInicial = db.Column(Date)
    FechaFinal = db.Column(Date)

    # Relaciones
    curso = relationship('Curso', back_populates='cronogramas', foreign_keys=[ID_Curso])
    periodo = relationship('Periodo', back_populates='cronogramas', foreign_keys=[ID_Periodo])
    actividades = relationship('Actividad', back_populates='cronograma', lazy='dynamic')


# -----------------------------------------------------
# Actividad
# -----------------------------------------------------
class Actividad(db.Model):
    __tablename__ = 'Actividad'
    ID_Actividad = db.Column(Integer, primary_key=True, autoincrement=True)
    Titulo = db.Column(String(200), nullable=False)
    Tipo = db.Column(Enum('Taller', 'Examen', 'Proyecto', 'Participacion', 'Grupo'))
    Fecha = db.Column(Date)
    ID_Cronograma_Actividades = db.Column(Integer, ForeignKey('Cronograma_Actividades.ID_Cronograma_Actividades'), nullable=False)
    Estado = db.Column(Enum('Pendiente', 'Calificada', 'Cancelada'))
    Porcentaje = db.Column(DECIMAL(5,2))

    # Relaciones
    cronograma = relationship('Cronograma_Actividades', back_populates='actividades', foreign_keys=[ID_Cronograma_Actividades])
    estudiantes = relationship('Actividad_Estudiante', back_populates='actividad', lazy='dynamic')


# -----------------------------------------------------
# Actividad_Estudiante
# -----------------------------------------------------
class Actividad_Estudiante(db.Model):
    __tablename__ = 'Actividad_Estudiante'
    ID_Actividad_Estudiante = db.Column(Integer, primary_key=True, autoincrement=True)
    ID_Actividad = db.Column(Integer, ForeignKey('Actividad.ID_Actividad'), nullable=False)
    ID_Matricula = db.Column(Integer, ForeignKey('Matricula.ID_Matricula'), nullable=False)
    Observaciones = db.Column(Text)
    Calificacion = db.Column(DECIMAL(5,2))

    # Relaciones
    actividad = relationship('Actividad', back_populates='estudiantes', foreign_keys=[ID_Actividad])
    matricula = relationship('Matricula', back_populates='actividades_estudiante', foreign_keys=[ID_Matricula])


# -----------------------------------------------------
# Observacion
# -----------------------------------------------------
class Observacion(db.Model):
    __tablename__ = 'Observacion'
    ID_Observacion = db.Column(Integer, primary_key=True, autoincrement=True)
    Fecha = db.Column(Date, nullable=False)
    Descripcion = db.Column(Text)
    Tipo = db.Column(Enum('Academica', 'Convivencial'))
    NivelImportancia = db.Column(Enum('Bajo', 'Medio', 'Alto'))
    Recomendacion = db.Column(Text)
    Estado = db.Column(Enum('Activa', 'Inactiva'))
    ID_Horario = db.Column(Integer, ForeignKey('Programacion.ID_Programacion'))
    ID_Matricula = db.Column(Integer, ForeignKey('Matricula.ID_Matricula'))

    # Relaciones
    programacion = relationship('Programacion', back_populates='observaciones', foreign_keys=[ID_Horario])
    matricula = relationship('Matricula', back_populates='observaciones', foreign_keys=[ID_Matricula])