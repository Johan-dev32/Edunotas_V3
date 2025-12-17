#!/usr/bin/env python3
"""
Script para crear cursos del 601 al 1103 con secciones 01, 02, 03
"""
import os
import sys
from datetime import datetime

# Agregar el directorio raíz del proyecto al path de Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from Controladores.models import Curso

def crear_cursos_masivos():
    """Crear cursos del 601 al 1103 con secciones 01, 02, 03"""
    
    with app.app_context():
        try:
            # Lista para almacenar todos los cursos a crear
            cursos_a_crear = []
            
            # Generar cursos del 601 al 1103
            for curso_num in range(601, 1104):  # 601 a 1103 inclusive
                for seccion in ['01', '02', '03']:
                    # Determinar el grado basado en el número
                    if 601 <= curso_num <= 603:
                        grado = "Primero"
                    elif 604 <= curso_num <= 606:
                        grado = "Segundo"
                    elif 607 <= curso_num <= 609:
                        grado = "Tercero"
                    elif 701 <= curso_num <= 703:
                        grado = "Cuarto"
                    elif 704 <= curso_num <= 706:
                        grado = "Quinto"
                    elif 707 <= curso_num <= 709:
                        grado = "Sexto"
                    elif 801 <= curso_num <= 803:
                        grado = "Séptimo"
                    elif 804 <= curso_num <= 806:
                        grado = "Octavo"
                    elif 807 <= curso_num <= 809:
                        grado = "Noveno"
                    elif 901 <= curso_num <= 903:
                        grado = "Décimo"
                    elif 904 <= curso_num <= 906:
                        grado = "Undécimo"
                    elif 1001 <= curso_num <= 1003:
                        grado = "Duodécimo"
                    elif 1101 <= curso_num <= 1103:
                        grado = "Tercer Año"
                    else:
                        grado = f"Grado {curso_num}"
                    
                    # Crear objeto Curso
                    nuevo_curso = Curso(
                        Grado=grado,
                        Grupo=seccion,
                        Anio="2025",  # Año actual
                        Estado="Activo",
                        DirectorGrupo=None  # Sin director por ahora
                    )
                    cursos_a_crear.append(nuevo_curso)
            
            # Verificar cuántos cursos ya existen
            cursos_existentes = Curso.query.all()
            cursos_existentes_ids = {c.ID_Curso for c in cursos_existentes}
            
            # Filtrar solo los cursos que no existen
            cursos_nuevos = [c for c in cursos_a_crear if c.ID_Curso not in cursos_existentes_ids]
            
            if cursos_nuevos:
                print(f"Creando {len(cursos_nuevos)} cursos nuevos...")
                
                # Agregar todos los cursos nuevos a la base de datos
                db.session.bulk_save_objects(cursos_nuevos)
                db.session.commit()
                
                print(f"✅ Se crearon {len(cursos_nuevos)} cursos exitosamente")
                print("Cursos creados:")
                for curso in cursos_nuevos[:10]:  # Mostrar primeros 10 como ejemplo
                    print(f"  - {curso.Grado} {curso.Grupo} (ID: {curso.ID_Curso})")
                if len(cursos_nuevos) > 10:
                    print(f"  ... y {len(cursos_nuevos) - 10} más")
            else:
                print("✅ Todos los cursos ya existen en la base de datos")
                
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error al crear cursos: {str(e)}")
            return False
            
        return True

if __name__ == "__main__":
    print("🚀 Iniciando creación masiva de cursos...")
    print(f"📅 Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    exito = crear_cursos_masivos()
    
    if exito:
        print("\n✅ Proceso completado exitosamente")
        print("📚 Ahora deberías ver los cursos en el sistema")
    else:
        print("\n❌ Ocurrió un error durante el proceso")
