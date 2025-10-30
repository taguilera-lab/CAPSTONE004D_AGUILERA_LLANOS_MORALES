from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from documents.models import FlotaUser, Role, Vehicle, UserStatus

class Command(BaseCommand):
    help = 'Crear usuarios de prueba para cada rol'

    def handle(self, *args, **options):
        roles = [
            'Jefe de Flota',
            'Mecánico',
            'Vendedor',
            'Guardia',
            'Bodeguero',
            'Supervisor',
            'Jefe de taller',
            'Recepcionista de Vehículos'
        ]

        # Obtener un vehículo de ejemplo (asumir que existe)
        vehicle = None
        try:
            vehicle = Vehicle.objects.first()
            if not vehicle:
                self.stdout.write(self.style.ERROR('No hay vehículos en la BD. Crea uno primero.'))
                return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error al obtener vehículo: {e}'))
            return

        # Obtener status de usuario (asumir que existe 'Activo')
        user_status = None
        try:
            user_status = UserStatus.objects.filter(name='Activo').first()
            if not user_status:
                user_status = UserStatus.objects.create(name='Activo', description='Usuario activo')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error al obtener/crear UserStatus: {e}'))
            return

        for role_name in roles:
            # Crear o obtener rol
            role, created = Role.objects.get_or_create(name=role_name)
            if created:
                self.stdout.write(f'Rol creado: {role_name}')

            # Crear usuario Django
            username = role_name.lower().replace(' ', '_')
            user, created = User.objects.get_or_create(username=username, defaults={'password': '123'})
            if created:
                user.set_password('123')
                user.save()
                self.stdout.write(f'Usuario creado: {username}')

            # Borrar FlotaUser existente si no tiene user asignado
            FlotaUser.objects.filter(name=role_name).delete()

            # Crear FlotaUser nuevo con user asignado
            flota_user = FlotaUser.objects.create(
                name=role_name,
                user=user,
                role=role,
                patent=vehicle,
                status=user_status,
                observations=f'Usuario de prueba para {role_name}',
                gpid=f'gpid_{username}'
            )
            self.stdout.write(f'FlotaUser creado: {role_name}')

        self.stdout.write(self.style.SUCCESS('Usuarios creados exitosamente.'))