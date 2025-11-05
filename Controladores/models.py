# models.py
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Date, Enum, Text, ForeignKey, Time
from sqlalchemy import Numeric as DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import YEAR
from datetime import datetime
from flask_login import UserMixin
from flask_login import UserMixin

db = SQLAlchemy()


# Definiciones de enums en Python para reutilizar (opcional)
EstadoEnum = ("Activo", "Inactivo")
GeneroEnum = ("M", "F", "Otro")
RolEnum = ("Administrador", "Docente", "Estudiante", "Acudiente")
EstadoNotifEnum = ("Leída", "No leída")
ParentescoEnum = ("Padre","Madre","Abuelo","Abuela","Tio","Tia","Primo","Prima")
EstadoCursoEnum = ("Activo","Inactivo")
EstadoAsignaturaEnum = ("Activa","Inactiva")
TipoActividadEnum = ("Taller","Examen","Proyecto","Participacion","Grupo")
EstadoActividadEnum = ("Pendiente","Calificada","Cancelada")
TipoObservacionEnum = ("Academica","Convivencial")
NivelImportanciaEnum = ("Bajo","Medio","Alto")
EstadoTutoriaEnum = ("Activo","Inactivo")  # not in SQL but keep generic

class Usuario(db.Model):
    __tablename__ = "Usuario"
    ID_Usuario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Nombre = db.Column(db.String(100), nullable=False)
    Apellido = db.Column(db.String(100), nullable=False)
    Correo = db.Column(db.String(150), nullable=False, unique=True)
    Contrasena = db.Column(db.String(255), nullable=False)
    TipoDocumento = db.Column(db.String(50))
    NumeroDocumento = db.Column(db.String(50), unique=True)
    Direccion = db.Column(db.String(200))
    Telefono = db.Column(db.String(50))
    Estado = db.Column(db.Enum(*EstadoEnum, name="estado_enum"), default="Activo")
    Genero = db.Column(db.Enum(*GeneroEnum, name="genero_enum"))
    Rol = db.Column(db.Enum(*RolEnum, name="rol_enum"), nullable=False)

    # Relaciones
    notificaciones = relationship("Notificacion", back_populates="usuario", cascade="all, delete-orphan")
    acudientes = relationship("Acudiente", back_populates="usuario", foreign_keys="Acudiente.ID_Usuario", cascade="all, delete-orphan")
    como_estudiante_acudiente = relationship("Acudiente", back_populates="estudiante", foreign_keys="Acudiente.ID_Estudiante")
    cursos_dirigidos = relationship("Curso", back_populates="director", foreign_keys="Curso.DirectorGrupo")
    docentes_asignaturas = relationship("Docente_Asignatura", back_populates="docente", foreign_keys="Docente_Asignatura.ID_Docente")
    programaciones_docente = relationship("Programacion", back_populates="docente", foreign_keys="Programacion.ID_Docente")
    matriculas = relationship("Matricula", back_populates="estudiante_usuario", foreign_keys="Matricula.ID_Estudiante")
    encuestas_creadas = relationship("Encuesta", back_populates="creador", foreign_keys="Encuesta.CreadoPor")
    noticias_creadas = relationship("Noticias", back_populates="creador", foreign_keys="Noticias.CreadoPor")
    enviados_citaciones = relationship("Citaciones", back_populates="enviado_por", foreign_keys="Citaciones.EnviadoPor")
    recibidos_citaciones = relationship("Citaciones", back_populates="destinatario", foreign_keys="Citaciones.ID_Usuario")
    reportes_docente = relationship("Reporte_Notas", back_populates="docente", foreign_keys="Reporte_Notas.ID_Docente")

class Notificacion(db.Model):
    __tablename__ = "Notificacion"
    ID_Notificacion = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Titulo = db.Column(db.String(150), nullable=False)
    Mensaje = db.Column(db.String(300), nullable=False)
    Enlace = db.Column(db.String(255))
    Estado = db.Column(db.Enum(*EstadoNotifEnum, name="estado_notif_enum"), default="No leída")
    Fecha = db.Column(db.DateTime, default=datetime.utcnow)
    ID_Usuario = db.Column(db.Integer, db.ForeignKey("Usuario.ID_Usuario", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)

    usuario = relationship("Usuario", back_populates="notificaciones")

class Acudiente(db.Model):
    __tablename__ = "Acudiente"
    ID_Acudiente = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ID_Usuario = db.Column(db.Integer, db.ForeignKey("Usuario.ID_Usuario", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    ID_Estudiante = db.Column(db.Integer, db.ForeignKey("Usuario.ID_Usuario", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    Parentesco = db.Column(db.Enum(*ParentescoEnum, name="parentesco_enum"))
    Estado = db.Column(db.Enum(*EstadoEnum, name="estado_acudiente_enum"), default="Activo")

    usuario = relationship("Usuario", back_populates="acudientes", foreign_keys=[ID_Usuario])
    estudiante = relationship("Usuario", back_populates="como_estudiante_acudiente", foreign_keys=[ID_Estudiante])

class Curso(db.Model):
    __tablename__ = "Curso"
    ID_Curso = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Grado = db.Column(db.String(10), nullable=False)
    Grupo = db.Column(db.String(10))
    Anio = db.Column(db.String(4), nullable=False)  # YEAR mapped to string of 4 chars
    Estado = db.Column(db.Enum(*EstadoCursoEnum, name="estado_curso_enum"), default="Activo")
    DirectorGrupo = db.Column(db.Integer, db.ForeignKey("Usuario.ID_Usuario", ondelete="SET NULL", onupdate="CASCADE"), nullable=True)

    director = relationship("Usuario", back_populates="cursos_dirigidos", foreign_keys=[DirectorGrupo])
    matriculas = relationship("Matricula", back_populates="curso", cascade="all, delete-orphan")
    programaciones = relationship("Programacion", back_populates="curso", cascade="all, delete-orphan")
    cronogramas = relationship("Cronograma_Actividades", back_populates="curso", cascade="all, delete-orphan")
    reuniones = relationship("Reuniones", back_populates="curso", foreign_keys="Reuniones.ID_Curso")

class Matricula(db.Model):
    __tablename__ = "Matricula"
    ID_Matricula = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ID_Estudiante = db.Column(db.Integer, db.ForeignKey("Usuario.ID_Usuario", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    ID_Curso = db.Column(db.Integer, db.ForeignKey("Curso.ID_Curso", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    Correo = db.Column(db.String(150))
    FechaNacimiento = db.Column(db.Date)
    DepNacimiento = db.Column(db.String(100))
    TipoDocumento = db.Column(db.String(50))
    NumeroDocumento = db.Column(db.String(50))
    AnioLectivo = db.Column(db.String(4), nullable=False)

    estudiante_usuario = relationship("Usuario", foreign_keys=[ID_Estudiante])
    curso = relationship("Curso", back_populates="matriculas")
    actividades_estudiante = relationship("Actividad_Estudiante", back_populates="matricula", cascade="all, delete-orphan")
    reportes = relationship("Reporte_Notas", back_populates="matricula", foreign_keys="Reporte_Notas.ID_Matricula")

class Periodo(db.Model):
    __tablename__ = "Periodo"
    ID_Periodo = db.Column(db.Integer, primary_key=True, autoincrement=True)
    NumeroPeriodo = db.Column(db.Integer, nullable=False)
    Anio = db.Column(db.String(4), nullable=False)
    FechaInicial = db.Column(db.Date)
    FechaFinal = db.Column(db.Date)

    cronogramas = relationship("Cronograma_Actividades", back_populates="periodo")
    reportes = relationship("Reporte_Notas", back_populates="periodo")

class Asignatura(db.Model):
    __tablename__ = "Asignatura"
    ID_Asignatura = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Nombre = db.Column(db.String(100), nullable=False)
    Descripcion = db.Column(db.Text)
    Grado = db.Column(db.String(10))
    Area = db.Column(db.String(100))
    CodigoAsignatura = db.Column(db.String(20), unique=True)
    Estado = db.Column(db.Enum(*EstadoAsignaturaEnum, name="estado_asignatura_enum"), default="Activa")

    docentes_asignaturas = relationship("Docente_Asignatura", back_populates="asignatura", cascade="all, delete-orphan")
    reportes_detalle = relationship("Reporte_Notas_Detalle", back_populates="asignatura")

class Docente_Asignatura(db.Model):
    __tablename__ = "Docente_Asignatura"
    ID_Docente_Asignatura = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ID_Docente = db.Column(db.Integer, db.ForeignKey("Usuario.ID_Usuario", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    ID_Asignatura = db.Column(db.Integer, db.ForeignKey("Asignatura.ID_Asignatura", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    ID_Curso = db.Column(db.Integer, db.ForeignKey("Curso.ID_Curso", ondelete="SET NULL", onupdate="CASCADE"), nullable=True)

    docente = relationship("Usuario", back_populates="docentes_asignaturas", foreign_keys=[ID_Docente])
    asignatura = relationship("Asignatura", back_populates="docentes_asignaturas")
    curso = relationship("Curso", foreign_keys=[ID_Curso])

class Bloques(db.Model):
    __tablename__ = "Bloques"
    ID_Bloque = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Nombre_Bloque = db.Column(db.String(50), nullable=False)
    HoraInicio = db.Column(db.Time, nullable=False)
    HoraFin = db.Column(db.Time, nullable=False)

    programaciones = relationship("Programacion", back_populates="bloque")

class Programacion(db.Model):
    __tablename__ = "Programacion"
    ID_Programacion = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ID_Curso = db.Column(db.Integer, db.ForeignKey("Curso.ID_Curso", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    ID_Docente_Asignatura = db.Column(db.Integer, db.ForeignKey("Docente_Asignatura.ID_Docente_Asignatura", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    HoraInicio = db.Column(db.Time)
    HoraFin = db.Column(db.Time)
    Dia = db.Column(db.String(20))
    ID_Docente = db.Column(db.Integer, db.ForeignKey("Usuario.ID_Usuario", ondelete="SET NULL", onupdate="CASCADE"), nullable=True)
    ID_Bloque = db.Column(db.Integer, db.ForeignKey("Bloques.ID_Bloque", ondelete="SET NULL", onupdate="CASCADE"), nullable=True)

    curso = relationship("Curso", back_populates="programaciones")
    docente_asignatura = relationship("Docente_Asignatura", foreign_keys=[ID_Docente_Asignatura])
    docente = relationship("Usuario", back_populates="programaciones_docente", foreign_keys=[ID_Docente])
    bloque = relationship("Bloques", back_populates="programaciones")

class Asistencia(db.Model):
    __tablename__ = "Asistencia"
    ID_Asistencia = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Fecha = db.Column(db.Date, nullable=False)
    ID_Programacion = db.Column(db.Integer, db.ForeignKey("Programacion.ID_Programacion", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)

    programacion = relationship("Programacion")
    detalles = relationship("Detalle_Asistencia", back_populates="asistencia", cascade="all, delete-orphan")

class Detalle_Asistencia(db.Model):
    __tablename__ = "Detalle_Asistencia"
    ID_Detalle_Asistencia = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ID_Asistencia = db.Column(db.Integer, db.ForeignKey("Asistencia.ID_Asistencia", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    ID_Estudiante = db.Column(db.Integer, db.ForeignKey("Usuario.ID_Usuario", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    Estado_Asistencia = db.Column(db.Enum('Presente','Ausente','Justificado', name="estado_asistencia_enum"))
    Observaciones = db.Column(db.Text)

    asistencia = relationship("Asistencia", back_populates="detalles")
    estudiante = relationship("Usuario")

class Cronograma_Actividades(db.Model):
    __tablename__ = "Cronograma_Actividades"
    ID_Cronograma_Actividades = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ID_Curso = db.Column(db.Integer, db.ForeignKey("Curso.ID_Curso", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    ID_Periodo = db.Column(db.Integer, db.ForeignKey("Periodo.ID_Periodo", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    FechaInicial = db.Column(db.Date)
    FechaFinal = db.Column(db.Date)

    curso = relationship("Curso", back_populates="cronogramas")
    periodo = relationship("Periodo", back_populates="cronogramas")
    actividades = relationship("Actividad", back_populates="cronograma", cascade="all, delete-orphan")

class Actividad(db.Model):
    __tablename__ = "Actividad"
    ID_Actividad = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Titulo = db.Column(db.String(200), nullable=False)
    Tipo = db.Column(db.Enum(*TipoActividadEnum, name="tipo_actividad_enum"))
    Fecha = db.Column(db.Date)
    Descripcion = db.Column(db.Text)
    Hora = db.Column(db.Time)
    ArchivoPDF = db.Column(db.String(255))
    ID_Cronograma_Actividades = db.Column(db.Integer, db.ForeignKey("Cronograma_Actividades.ID_Cronograma_Actividades", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    Estado = db.Column(db.Enum(*EstadoActividadEnum, name="estado_actividad_enum"), default="Pendiente")
    Porcentaje = db.Column(db.Numeric(5,2))

    cronograma = relationship("Cronograma_Actividades", back_populates="actividades")
    participaciones = relationship("Actividad_Estudiante", back_populates="actividad", cascade="all, delete-orphan")

class Actividad_Estudiante(db.Model):
    __tablename__ = "Actividad_Estudiante"
    ID_Actividad_Estudiante = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ID_Actividad = db.Column(db.Integer, db.ForeignKey("Actividad.ID_Actividad", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    ID_Matricula = db.Column(db.Integer, db.ForeignKey("Matricula.ID_Matricula", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    Observaciones = db.Column(db.Text)
    Calificacion = db.Column(db.Numeric(5,2))

    actividad = relationship("Actividad", back_populates="participaciones")
    matricula = relationship("Matricula", back_populates="actividades_estudiante")

class Observacion(db.Model):
    __tablename__ = "Observacion"
    ID_Observacion = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Fecha = db.Column(db.Date, nullable=False)
    Descripcion = db.Column(db.Text)
    Tipo = db.Column(db.Enum(*TipoObservacionEnum, name="tipo_observacion_enum"))
    NivelImportancia = db.Column(db.Enum(*NivelImportanciaEnum, name="nivel_importancia_enum"))
    Recomendacion = db.Column(db.Text)
    Estado = db.Column(db.Enum(*EstadoEnum, name="estado_observacion_enum"), default="Activa")
    ID_Programacion = db.Column(db.Integer, db.ForeignKey("Programacion.ID_Programacion", ondelete="SET NULL", onupdate="CASCADE"), nullable=True)
    ID_Matricula = db.Column(db.Integer, db.ForeignKey("Matricula.ID_Matricula", ondelete="SET NULL", onupdate="CASCADE"), nullable=True)
    ID_Estudiante = db.Column(db.Integer, db.ForeignKey("Usuario.ID_Usuario", ondelete="SET NULL", onupdate="CASCADE"), nullable=True)

    programacion = relationship("Programacion")
    matricula = relationship("Matricula")
    estudiante = relationship("Usuario")

class Tutorias(db.Model):
    __tablename__ = "Tutorias"
    ID_Tutoria = db.Column(db.Integer, primary_key=True, autoincrement=True)
    NombreCompleto = db.Column(db.String(200), nullable=False)
    Rol = db.Column(db.String(50))
    Tema = db.Column(db.String(255))
    FechaRealizacion = db.Column(db.DateTime)
    ID_Curso = db.Column(db.Integer, db.ForeignKey("Curso.ID_Curso", ondelete="SET NULL", onupdate="CASCADE"), nullable=True)
    ID_Estudiante = db.Column(db.Integer, db.ForeignKey("Usuario.ID_Usuario", ondelete="SET NULL", onupdate="CASCADE"), nullable=True)
    Correo = db.Column(db.String(150))
    Motivo = db.Column(db.Text)
    Observaciones = db.Column(db.Text)

    curso = relationship("Curso")
    estudiante = relationship("Usuario")

class Reuniones(db.Model):
    __tablename__ = "Reuniones"
    ID_Reunion = db.Column(db.Integer, primary_key=True, autoincrement=True)
    FechaReunion = db.Column(db.DateTime, nullable=False)
    TemaATratar = db.Column(db.String(255))
    NombreOrganizador = db.Column(db.String(200))
    CargoOrganizador = db.Column(db.String(100))
    NombresInvitados = db.Column(db.Text)
    LinkReunion = db.Column(db.String(300))
    ID_Curso = db.Column(db.Integer, db.ForeignKey("Curso.ID_Curso", ondelete="SET NULL", onupdate="CASCADE"), nullable=True)

    curso = relationship("Curso", back_populates="reuniones")

class Encuesta(db.Model):
    __tablename__ = "Encuesta"
    ID_Encuesta = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Titulo = db.Column(db.String(200), nullable=False)
    Descripcion = db.Column(db.Text)
    FechaCreacion = db.Column(db.DateTime, default=datetime.utcnow)
    FechaCierre = db.Column(db.DateTime, nullable=True)
    CreadoPor = db.Column(db.Integer, db.ForeignKey("Usuario.ID_Usuario", ondelete="SET NULL", onupdate="CASCADE"), nullable=True)
    DirigidoA = db.Column(db.Enum('Docente','Estudiante','Acudiente', name="dirigido_enum"), nullable=False)
    Archivo = db.Column(db.String(255))
    Activa = db.Column(db.Boolean, default=True)

    creador = relationship("Usuario", back_populates="encuestas_creadas", foreign_keys=[CreadoPor])
    preguntas = relationship("Encuesta_Pregunta", back_populates="encuesta", cascade="all, delete-orphan")
    respuestas = relationship("Encuesta_Respuesta", back_populates="encuesta", cascade="all, delete-orphan")

class Encuesta_Pregunta(db.Model):
    __tablename__ = "Encuesta_Pregunta"
    ID_Pregunta = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ID_Encuesta = db.Column(db.Integer, db.ForeignKey("Encuesta.ID_Encuesta", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    TextoPregunta = db.Column(db.Text, nullable=False)
    TipoRespuesta = db.Column(db.Enum('Texto','OpcionSimple','OpcionMultiple','Escala', name="tipo_respuesta_enum"), default="Texto")

    encuesta = relationship("Encuesta", back_populates="preguntas")
    respuestas = relationship("Encuesta_Respuesta", back_populates="pregunta", cascade="all, delete-orphan")

class Encuesta_Respuesta(db.Model):
    __tablename__ = "Encuesta_Respuesta"
    ID_Respuesta = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ID_Pregunta = db.Column(db.Integer, db.ForeignKey("Encuesta_Pregunta.ID_Pregunta", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    ID_Usuario = db.Column(db.Integer, db.ForeignKey("Usuario.ID_Usuario", ondelete="SET NULL", onupdate="CASCADE"), nullable=True)
    ID_Matricula = db.Column(db.Integer, db.ForeignKey("Matricula.ID_Matricula", ondelete="SET NULL", onupdate="CASCADE"), nullable=True)
    ID_Encuesta = db.Column(db.Integer, db.ForeignKey("Encuesta.ID_Encuesta", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    Respuesta = db.Column(db.Text)
    FechaRespuesta = db.Column(db.DateTime, default=datetime.utcnow)

    pregunta = relationship("Encuesta_Pregunta", back_populates="respuestas")
    usuario = relationship("Usuario")
    matricula = relationship("Matricula")
    encuesta = relationship("Encuesta", viewonly=True, secondary="Encuesta_Pregunta", primaryjoin="Encuesta_Pregunta.ID_Pregunta==Encuesta_Respuesta.ID_Pregunta")

class Noticias(db.Model):
    __tablename__ = "Noticias"
    ID_Noticia = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Fecha = db.Column(db.DateTime, default=datetime.utcnow)
    CreadoPor = db.Column(db.Integer, db.ForeignKey("Usuario.ID_Usuario", ondelete="SET NULL", onupdate="CASCADE"), nullable=True)
    Titulo = db.Column(db.String(255), nullable=False)
    Archivo = db.Column(db.String(255))
    Redaccion = db.Column(db.Text)

    creador = relationship("Usuario", back_populates="noticias_creadas")

class Reporte_Notas(db.Model):
    __tablename__ = "Reporte_Notas"
    ID_Reporte = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ID_Matricula = db.Column(db.Integer, db.ForeignKey("Matricula.ID_Matricula", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    ID_Curso = db.Column(db.Integer, db.ForeignKey("Curso.ID_Curso", ondelete="SET NULL", onupdate="CASCADE"), nullable=True)
    ID_Periodo = db.Column(db.Integer, db.ForeignKey("Periodo.ID_Periodo", ondelete="SET NULL", onupdate="CASCADE"), nullable=True)
    ID_Asignatura = db.Column(db.Integer, db.ForeignKey("Asignatura.ID_Asignatura", ondelete="SET NULL", onupdate="CASCADE"), nullable=True)
    ID_Docente = db.Column(db.Integer, db.ForeignKey("Usuario.ID_Usuario", ondelete="SET NULL", onupdate="CASCADE"), nullable=True)
    Fecha = db.Column(db.DateTime, default=datetime.utcnow)
    ObservacionesDocente = db.Column(db.Text)
    ArchivoPDF = db.Column(db.String(255))
    PromedioGeneral = db.Column(db.Numeric(5,2))

    matricula = relationship("Matricula", back_populates="reportes")
    curso = relationship("Curso")
    periodo = relationship("Periodo", back_populates="reportes")
    asignatura = relationship("Asignatura")
    docente = relationship("Usuario", back_populates="reportes_docente", foreign_keys=[ID_Docente])
    detalles = relationship("Reporte_Notas_Detalle", back_populates="reporte", cascade="all, delete-orphan")

class Reporte_Notas_Detalle(db.Model):
    __tablename__ = "Reporte_Notas_Detalle"
    ID_Detalle = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ID_Reporte = db.Column(db.Integer, db.ForeignKey("Reporte_Notas.ID_Reporte", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    ID_Asignatura = db.Column(db.Integer, db.ForeignKey("Asignatura.ID_Asignatura", ondelete="SET NULL", onupdate="CASCADE"), nullable=True)
    Nota1 = db.Column(db.Numeric(5,2))
    Nota2 = db.Column(db.Numeric(5,2))
    Nota3 = db.Column(db.Numeric(5,2))
    Nota4 = db.Column(db.Numeric(5,2))
    Promedio = db.Column(db.Numeric(5,2))
    Observacion = db.Column(db.String(255))

    reporte = relationship("Reporte_Notas", back_populates="detalles")
    asignatura = relationship("Asignatura", back_populates="reportes_detalle")

class Estudiantes_Repitentes(db.Model):
    __tablename__ = "Estudiantes_Repitentes"
    ID_Repitente = db.Column(db.Integer, primary_key=True, autoincrement=True)
    TipoDocumento = db.Column(db.String(50))
    NumeroDocumento = db.Column(db.String(50))
    NombreCompleto = db.Column(db.String(200))
    Veces = db.Column(db.Integer, default=1)
    ID_Matricula = db.Column(db.Integer, db.ForeignKey("Matricula.ID_Matricula", ondelete="SET NULL", onupdate="CASCADE"), nullable=True)
    Matriculado = db.Column(db.Boolean, default=False)

    matricula = relationship("Matricula")

class Historial_Academico(db.Model):
    __tablename__ = "Historial_Academico"
    ID_Historial = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ID_Matricula = db.Column(db.Integer, db.ForeignKey("Matricula.ID_Matricula", ondelete="SET NULL", onupdate="CASCADE"), nullable=True)
    Anio = db.Column(db.String(4))
    Periodo = db.Column(db.String(50))
    Descripcion = db.Column(db.Text)
    Observaciones = db.Column(db.Text)
    Archivo = db.Column(db.String(255))
    CreadoEn = db.Column(db.DateTime, default=datetime.utcnow)

    matricula = relationship("Matricula")

class Citaciones(db.Model):
    __tablename__ = "Citaciones"
    ID_Citacion = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Fecha = db.Column(db.DateTime, nullable=False)
    Correo = db.Column(db.String(150))
    Asunto = db.Column(db.String(255))
    RedaccionCitacion = db.Column(db.Text)
    ID_Usuario = db.Column(db.Integer, db.ForeignKey("Usuario.ID_Usuario", ondelete="SET NULL", onupdate="CASCADE"), nullable=True)
    EnviadoPor = db.Column(db.Integer, db.ForeignKey("Usuario.ID_Usuario", ondelete="SET NULL", onupdate="CASCADE"), nullable=True)
    Estado = db.Column(db.Enum('Pendiente','Enviada','Atendida', name="estado_citacion_enum"), default="Pendiente")

    destinatario = relationship("Usuario", back_populates="recibidos_citaciones", foreign_keys=[ID_Usuario])
    enviado_por = relationship("Usuario", back_populates="enviados_citaciones", foreign_keys=[EnviadoPor])

