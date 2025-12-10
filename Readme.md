# EduNotas V3

> **EduNotas** es un sistema web de gestión académica que centraliza la administración de notas, asistencia y el rendimiento académico de los estudiantes. Facilita el seguimiento escolar de forma clara, rápida y organizada para toda la comunidad educativa.

---

## Objetivo del Proyecto

Desarrollar una plataforma web integral, mediante la automatización e integración de los procesos académicos y administrativos del colegio **Fe y Alegría José María Velaz**, con el fin de optimizar la comunicación entre docentes, estudiantes, padres y directivos, mejorando la eficiencia, la trazabilidad y la toma de decisiones institucionales.

---

##  Funcionalidades Principales

El sistema EduNotas se estructura en módulos clave que cubren el ciclo académico:

### 1.  Gestión de Notas y Rendimiento Académico (Núcleo)
* Registro de notas por parte del docente.
* Control de notas por periodo académico.
* Cálculo automático de promedios.
* Consulta de notas y visualización del historial académico por estudiante.

### 2.  Gestión de Usuarios y Roles (Acceso y Seguridad)
* Sistema de **Inicio de Sesión** seguro.
* Gestión de **roles y permisos** (Administrador, Docente, Estudiante, Acudiente).
* Registro inicial, administrativo y actualización de perfiles.
* Recuperación de contraseñas.

### 3.  Gestión de Tareas y Asistencia
* Registro de tareas y actividades por parte del docente.
* Subida de evidencias y visualización del historial de entregas por parte del estudiante.
* Registro de asistencia e inasistencia, incluyendo la justificación de permisos.

### 4.  Registro Académico Básico
* Gestión de **Cursos** y **Asignaturas**.
* Registro de **Estudiantes** y **Docentes**.

### 5.  Generación de Información y Reportes
* Generación de reportes generales.
* Informe de desempeño académico por grupo.
* Reportes de asistencia por materia y docente.

---

##  Roles del Sistema

| Rol | Funcionalidad Principal |
| :--- | :--- |
| **Administrador** | Gestiona usuarios, cursos, asignaturas y la configuración general del sistema. |
| **Docente** | Registra notas, asistencia, tareas y realiza el seguimiento académico. |
| **Estudiante** | Consulta notas, actividades, historial académico y sube evidencias. |
| **Acudiente** | Visualiza el rendimiento académico y la asistencia del estudiante a su cargo. |

---

##  Tecnologías Utilizadas

| Categoría | Herramientas |
| :--- | :--- |
| **Backend** | Python  |
| **Frontend** | HTML, CSS, JavaScript |
| **Base de Datos** | MySQL |
| **Control de Versiones** | Git |

---

##  Instalación y Ejecución Local

Pasos para levantar el proyecto en tu entorno de desarrollo:

1.  **Clonar el repositorio:**
    ```bash
    git clone <URL_DEL_REPOSITORIO>
    cd EDUNOTAS_V3
    ```

2.  **Instalar las dependencias de Python:**
    Asegúrate de tener Python instalado.
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configuración de la Base de Datos y Variables de Entorno:**
    * Asegúrate de tener un servidor MySQL en ejecución.
    * Configura las credenciales de conexión a la base de datos en el archivo `config.py`.

4.  **Ejecutar la Aplicación:**
    ```bash
    python app.py
    ```
    La aplicación estará disponible en `http://127.0.0.1:5000/` .

---

##  Estructura del Proyecto
EDUNOTAS_V3/
│── __pycache__/
│── .vscode/
│── controladores/
│   ├── models.py
│── routes/
│   ├── Acudiente.py
│   ├── Administrador.py
│   ├── Docente.py
│   ├── Estudiante.py
│   ├── notificaciones_routes.py
│── static/
│   ├── css/
│   ├── img/
│   ├── js/
│   ├── uploads/
│── templates/
│   ├── Acudiente/
│   ├── Administrador/
│   ├── Docentes/
│   ├── Estudiante/
│   ├── base.html
│   ├── Login.html
│   ├── perfil.html
│── app.py
│── config.py
│── requirements.py


##  Autores
- Ricardo Betancourt Limas
- Sonia Gisell Leal Abello
- Johan Andres Tamara Salas
- Juan Camilo Rivera Duquino


##  Creditos
Un proyecto hecho con mucho amor y peleas internas :O, pero fue divertido
Donar a este número a Nequi: 3203541891 porfavor

No pelien mas