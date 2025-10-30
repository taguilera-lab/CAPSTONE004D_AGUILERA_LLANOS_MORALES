#!/usr/bin/env python3
"""
Script para resetear completamente la base de datos SQLite
Elimina el archivo de base de datos sin usar migraciones
"""
import os
import sys

def reset_database():
    """Elimina completamente la base de datos SQLite"""

    # Ruta al archivo de base de datos
    db_path = os.path.join(os.path.dirname(__file__), 'db.sqlite3')

    # Verificar si existe el archivo
    if os.path.exists(db_path):
        try:
            # Eliminar el archivo
            os.remove(db_path)
            print(f"✅ Base de datos eliminada: {db_path}")
            print("🗑️  Todos los datos han sido borrados permanentemente")
        except Exception as e:
            print(f"❌ Error al eliminar la base de datos: {e}")
            return False
    else:
        print(f"ℹ️  La base de datos no existe: {db_path}")

    print("\n📝 Para recrear la estructura de la base de datos, ejecuta:")
    print("   python3 manage.py migrate")
    print("\n📝 Para poblar con datos de prueba, ejecuta:")
    print("   python3 populate_db.py")
    print("   python3 populate_work_orders.py")
    print("   python3 create_work_orders.py")

    return True

if __name__ == '__main__':
    print("🔄 Reseteando base de datos...")
    print("=" * 50)

    success = reset_database()

    if success:
        print("\n✅ Reset completado exitosamente!")
    else:
        print("\n❌ Error durante el reset")
        sys.exit(1)