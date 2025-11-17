#!/usr/bin/env python3
"""
Script completo para resetear y repoblar la base de datos
con los nuevos cambios del modelo
"""
import os
import sys
import subprocess

def run_command(command, description):
    """Ejecuta un comando y maneja errores"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completado")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en {description}: {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False

def main():
    """Proceso completo de reset y repoblado"""

    print("🚀 Iniciando reset y repoblado completo de la base de datos")
    print("=" * 60)

    # Cambiar al directorio del proyecto
    project_dir = os.path.dirname(__file__)
    os.chdir(project_dir)

    # Paso 1: Resetear base de datos
    if not run_command("python3 reset_db.py", "Reseteando base de datos"):
        return False

    # Paso 2: Crear migraciones
    if not run_command("python3 manage.py makemigrations", "Creando migraciones"):
        return False

    # Paso 3: Aplicar migraciones
    if not run_command("python3 manage.py migrate", "Aplicando migraciones"):
        return False

    # Paso 4: Poblar datos básicos
    if not run_command("python3 populate_db.py", "Poblando datos básicos"):
        return False

    # Paso 5: Crear estados de órdenes de trabajo
    if not run_command("python3 populate_work_orders.py", "Creando estados de OT"):
        return False

    # Paso 6: Crear órdenes de trabajo
    if not run_command("python3 create_work_orders.py", "Creando órdenes de trabajo"):
        return False

    # Paso 7: Migrar datos (asignar work_orders y service_types)
    if not run_command("python3 migrate_data.py", "Migrando datos del modelo"):
        return False

    print("\n" + "=" * 60)
    print("🎉 ¡Reset y repoblado completado exitosamente!")
    print("\n📊 Resumen:")
    print("   ✅ Base de datos reseteada")
    print("   ✅ Estructura recreada con nuevos modelos")
    print("   ✅ Datos de prueba cargados")
    print("   ✅ Órdenes de trabajo creadas")
    print("   ✅ Datos migrados correctamente")
    print("\n🚀 La aplicación está lista para usar!")

    return True

if __name__ == '__main__':
    success = main()
    if not success:
        print("\n❌ El proceso falló. Revisa los errores arriba.")
        sys.exit(1)