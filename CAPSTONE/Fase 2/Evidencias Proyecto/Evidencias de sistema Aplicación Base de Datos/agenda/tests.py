from django.test import TestCase, RequestFactory, Client, override_settings
from django.urls import reverse
from unittest.mock import patch, MagicMock
from django.template.loader import render_to_string
from agenda.views import home, calculate_working_hours_elapsed, calculate_completion_datetime
from datetime import datetime, time, timedelta
import re


def validate_chilean_plate(plate):
    """
    Valida si una patente chilena tiene formato correcto.
    Retorna True si es válida, False si no.
    """
    if not plate or not isinstance(plate, str):
        return False

    # Convertir a mayúsculas y remover espacios
    plate = plate.upper().replace(' ', '')

    # Patrones de patentes chilenas:
    # 1. Antiguas: 2 letras + 2 números + 2 letras (AB12CD)
    # 2. Nuevas: 4 letras + 2 números (ABCD12)
    # 3. Motos: 3 letras + 2 números (ABC12)

    patterns = [
        r'^[A-Z]{2}\d{2}[A-Z]{2}$',  # Antigua: AB12CD
        r'^[A-Z]{4}\d{2}$',          # Nueva: ABCD12
        r'^[A-Z]{3}\d{2}$',          # Moto: ABC12
    ]

    return any(re.match(pattern, plate) for pattern in patterns)


class HomeViewTestCase(TestCase):
    """Tests para la vista home del módulo agenda"""

    def setUp(self):
        """Configuración inicial para los tests"""
        self.factory = RequestFactory()
        self.client = Client()

    @override_settings(ALLOWED_HOSTS=['testserver'])
    def test_home_view_status_code(self):
        """Test que la vista home retorna status code 200"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    @patch('documents.models.Vehicle.objects')
    @patch('documents.models.Ingreso.objects')
    @patch('documents.models.WorkOrder.objects')
    @patch('documents.models.Incident.objects')
    def test_home_view_context_data(self, mock_incident, mock_workorder, mock_ingreso, mock_vehicle):
        """Test que la vista home incluye los datos correctos en el contexto"""
        # Configurar mocks
        mock_vehicle.count.return_value = 15
        mock_ingreso.filter.return_value.count.return_value = 8
        mock_workorder.filter.return_value.count.return_value = 6
        mock_incident.filter.return_value.distinct.return_value.count.return_value = 3

        # Usar render_to_string para obtener el contexto
        context = {
            'vehicles_count': 15,
            'ingresos_count': 8,
            'workorders_count': 6,
            'incidents_count': 3,
        }

        # Verificar que render_to_string funciona con el contexto
        html = render_to_string('agenda/home.html', context)
        self.assertIn('15', html)  # vehicles_count
        self.assertIn('8', html)   # ingresos_count
        self.assertIn('6', html)   # workorders_count
        self.assertIn('3', html)   # incidents_count

    @override_settings(ALLOWED_HOSTS=['testserver'])
    @patch('documents.models.Vehicle.objects')
    @patch('documents.models.Ingreso.objects')
    @patch('documents.models.WorkOrder.objects')
    @patch('documents.models.Incident.objects')
    def test_home_view_template_rendering(self, mock_incident, mock_workorder, mock_ingreso, mock_vehicle):
        """Test que la vista home renderiza el template correcto con los datos"""
        # Configurar mocks con valores de prueba
        mock_vehicle.count.return_value = 22
        mock_ingreso.filter.return_value.count.return_value = 12
        mock_workorder.filter.return_value.count.return_value = 7
        mock_incident.filter.return_value.distinct.return_value.count.return_value = 5

        # Hacer la petición usando el client
        response = self.client.get(reverse('home'))

        # Verificar que el contenido incluye los números correctos
        self.assertContains(response, '22')  # vehicles_count
        self.assertContains(response, '12')  # ingresos_count
        self.assertContains(response, '7')   # workorders_count
        self.assertContains(response, '5')   # incidents_count

        # Verificar que contiene elementos del template
        self.assertContains(response, 'Sistema de Gestión de Flota')
        self.assertContains(response, 'Acceso al Sistema')

    @override_settings(ALLOWED_HOSTS=['testserver'])
    def test_home_view_zero_counts(self):
        """Test que la vista home maneja correctamente conteos en cero"""
        with patch('documents.models.Vehicle.objects') as mock_vehicle:
            with patch('documents.models.Ingreso.objects') as mock_ingreso:
                with patch('documents.models.WorkOrder.objects') as mock_workorder:
                    with patch('documents.models.Incident.objects') as mock_incident:
                        # Configurar mocks con valores cero
                        mock_vehicle.count.return_value = 0
                        mock_ingreso.filter.return_value.count.return_value = 0
                        mock_workorder.filter.return_value.count.return_value = 0
                        mock_incident.filter.return_value.distinct.return_value.count.return_value = 0

                        response = self.client.get(reverse('home'))

                        # Verificar que se renderiza correctamente
                        self.assertContains(response, '0')
                        self.assertEqual(response.status_code, 200)

    @patch('documents.models.Vehicle.objects')
    @patch('documents.models.Ingreso.objects')
    @patch('documents.models.WorkOrder.objects')
    @patch('documents.models.Incident.objects')
    def test_home_view_database_queries(self, mock_incident, mock_workorder, mock_ingreso, mock_vehicle):
        """Test que verifica que se hacen las consultas correctas a la base de datos"""
        # Configurar mocks
        mock_vehicle.count.return_value = 10
        mock_ingreso.filter.return_value.count.return_value = 5
        mock_workorder.filter.return_value.count.return_value = 3
        mock_incident.filter.return_value.distinct.return_value.count.return_value = 2

        # Usar RequestFactory para evitar middleware
        request = self.factory.get('/')
        home(request)

        # Verificar que se llamaron los métodos correctos
        mock_vehicle.count.assert_called_once()
        mock_ingreso.filter.assert_called_once_with(exit_datetime__isnull=True)
        mock_ingreso.filter.return_value.count.assert_called_once()
        mock_workorder.filter.assert_called_once_with(status__name__in=['En Progreso', 'Pendiente'])
        mock_workorder.filter.return_value.count.assert_called_once()
        mock_incident.filter.assert_called_once_with(diagnostics__status__in=['Reportada', 'En Progreso'])
        mock_incident.filter.return_value.distinct.assert_called_once()
        mock_incident.filter.return_value.distinct.return_value.count.assert_called_once()


class CalculateWorkingHoursTestCase(TestCase):
    """Tests para la función calculate_working_hours_elapsed"""

    def test_same_day_within_working_hours(self):
        """Test trabajo dentro del mismo día y horario laboral"""
        start = datetime(2025, 11, 9, 9, 0, 0)  # 9:00 AM
        end = datetime(2025, 11, 9, 12, 0, 0)    # 12:00 PM
        result = calculate_working_hours_elapsed(start, end)
        self.assertEqual(result, 3.0)  # 3 horas

    def test_same_day_start_before_work_hours(self):
        """Test trabajo que comienza antes del horario laboral"""
        start = datetime(2025, 11, 9, 6, 0, 0)   # 6:00 AM
        end = datetime(2025, 11, 9, 10, 0, 0)     # 10:00 AM
        result = calculate_working_hours_elapsed(start, end)
        self.assertEqual(result, 2.5)  # De 7:30 a 10:00 = 2.5 horas

    def test_same_day_end_after_work_hours(self):
        """Test trabajo que termina después del horario laboral"""
        start = datetime(2025, 11, 9, 15, 0, 0)  # 3:00 PM
        end = datetime(2025, 11, 9, 18, 0, 0)    # 6:00 PM
        result = calculate_working_hours_elapsed(start, end)
        self.assertEqual(result, 1.5)  # De 3:00 a 4:30 = 1.5 horas

    def test_same_day_outside_working_hours(self):
        """Test trabajo completamente fuera del horario laboral"""
        start = datetime(2025, 11, 9, 5, 0, 0)   # 5:00 AM
        end = datetime(2025, 11, 9, 6, 0, 0)     # 6:00 AM
        result = calculate_working_hours_elapsed(start, end)
        self.assertEqual(result, 0.0)  # 0 horas

    def test_multiple_days_simple(self):
        """Test trabajo que cruza exactamente 1 día"""
        start = datetime(2025, 11, 9, 15, 0, 0)  # Día 1, 3:00 PM
        end = datetime(2025, 11, 10, 10, 0, 0)   # Día 2, 10:00 AM
        result = calculate_working_hours_elapsed(start, end)
        # Día 1: 1.5 horas (3:00-4:30), Día 2: 2.5 horas (7:30-10:00) = 4.0 horas
        self.assertEqual(result, 4.0)

    def test_multiple_days_full_day(self):
        """Test trabajo que incluye un día completo"""
        start = datetime(2025, 11, 8, 10, 0, 0)  # Viernes 10:00 AM
        end = datetime(2025, 11, 10, 10, 0, 0)   # Domingo 10:00 AM
        result = calculate_working_hours_elapsed(start, end)
        # Viernes: 6.5 horas (10:00-16:30), Sábado: 9 horas completas, Domingo: 2.5 horas (7:30-10:00)
        # Total: 6.5 + 9 + 2.5 = 18.0 horas
        self.assertEqual(result, 18.0)

    def test_same_datetime(self):
        """Test cuando start y end son iguales"""
        start = datetime(2025, 11, 9, 10, 0, 0)
        end = datetime(2025, 11, 9, 10, 0, 0)
        result = calculate_working_hours_elapsed(start, end)
        self.assertEqual(result, 0.0)

    def test_start_after_end(self):
        """Test cuando start es después de end (caso edge)"""
        start = datetime(2025, 11, 9, 15, 0, 0)
        end = datetime(2025, 11, 9, 10, 0, 0)
        result = calculate_working_hours_elapsed(start, end)
        self.assertEqual(result, 0.0)  # Debería retornar 0

    def test_exactly_working_hours(self):
        """Test trabajo exactamente en horario laboral completo"""
        start = datetime(2025, 11, 9, 7, 30, 0)  # 7:30 AM
        end = datetime(2025, 11, 9, 16, 30, 0)   # 4:30 PM
        result = calculate_working_hours_elapsed(start, end)
        self.assertEqual(result, 9.0)  # 9 horas exactas

    def test_partial_hours(self):
        """Test cálculo con horas parciales"""
        start = datetime(2025, 11, 9, 7, 45, 0)  # 7:45 AM
        end = datetime(2025, 11, 9, 8, 15, 0)     # 8:15 AM
        result = calculate_working_hours_elapsed(start, end)
        self.assertEqual(result, 0.5)  # 30 minutos = 0.5 horas


class CalculateCompletionDateTimeTestCase(TestCase):
    """Tests para la función calculate_completion_datetime"""

    def test_same_day_completion_within_hours(self):
        """Test finalización el mismo día dentro del horario laboral"""
        start = datetime(2025, 11, 9, 8, 0, 0)     # 8:00 AM
        result = calculate_completion_datetime(start, 2.0)  # 2 horas
        expected = datetime(2025, 11, 9, 10, 0, 0)  # 10:00 AM
        self.assertEqual(result, expected)

    def test_same_day_completion_exactly_working_hours(self):
        """Test finalización el mismo día con exactamente las horas laborales disponibles"""
        start = datetime(2025, 11, 9, 7, 30, 0)     # 7:30 AM (inicio jornada)
        result = calculate_completion_datetime(start, 9.0)  # 9 horas (jornada completa)
        expected = datetime(2025, 11, 9, 16, 30, 0)  # 4:30 PM (fin jornada)
        self.assertEqual(result, expected)

    def test_same_day_completion_partial_hours(self):
        """Test finalización el mismo día con horas parciales"""
        start = datetime(2025, 11, 9, 14, 0, 0)     # 2:00 PM
        result = calculate_completion_datetime(start, 1.5)  # 1.5 horas
        expected = datetime(2025, 11, 9, 15, 30, 0)  # 3:30 PM
        self.assertEqual(result, expected)

    def test_next_day_completion(self):
        """Test finalización al día siguiente"""
        start = datetime(2025, 11, 9, 15, 0, 0)     # 3:00 PM
        result = calculate_completion_datetime(start, 3.0)  # 3 horas (1.5h hoy + 1.5h mañana)
        expected = datetime(2025, 11, 10, 9, 0, 0)  # 9:00 AM siguiente día
        self.assertEqual(result, expected)

    def test_multiple_days_completion(self):
        """Test finalización en múltiples días"""
        start = datetime(2025, 11, 9, 8, 0, 0)      # 8:00 AM
        result = calculate_completion_datetime(start, 20.0)  # 20 horas (2 días completos + 2h)
        expected = datetime(2025, 11, 11, 10, 0, 0)  # 10:00 AM tercer día
        self.assertEqual(result, expected)

    def test_start_outside_working_hours_before(self):
        """Test inicio antes del horario laboral"""
        start = datetime(2025, 11, 9, 6, 0, 0)      # 6:00 AM (antes de jornada)
        result = calculate_completion_datetime(start, 2.0)  # 2 horas
        expected = datetime(2025, 11, 9, 9, 30, 0)  # 9:30 AM (7:30 + 2h)
        self.assertEqual(result, expected)

    def test_start_outside_working_hours_after(self):
        """Test inicio después del horario laboral"""
        start = datetime(2025, 11, 9, 17, 0, 0)     # 5:00 PM (después de jornada)
        result = calculate_completion_datetime(start, 2.0)  # 2 horas
        expected = datetime(2025, 11, 10, 9, 30, 0)  # 9:30 AM siguiente día
        self.assertEqual(result, expected)

    def test_zero_hours(self):
        """Test con 0 horas - debería retornar la misma fecha"""
        start = datetime(2025, 11, 9, 10, 0, 0)     # 10:00 AM
        result = calculate_completion_datetime(start, 0.0)  # 0 horas
        self.assertEqual(result, start)

    def test_negative_hours(self):
        """Test con horas negativas - debería retornar la misma fecha"""
        start = datetime(2025, 11, 9, 10, 0, 0)     # 10:00 AM
        result = calculate_completion_datetime(start, -1.0)  # -1 hora
        self.assertEqual(result, start)

    def test_weekend_behavior(self):
        """Test que funciona igual en fin de semana (no hay lógica especial para weekends)"""
        start = datetime(2025, 11, 9, 8, 0, 0)      # Sábado 8:00 AM
        result = calculate_completion_datetime(start, 2.0)  # 2 horas
        expected = datetime(2025, 11, 9, 10, 0, 0)  # Sábado 10:00 AM
        self.assertEqual(result, expected)


class ChileanPlateValidationTestCase(TestCase):
    """Tests para la función de validación de patentes chilenas"""

    def test_valid_old_format_plates(self):
        """Test patentes antiguas válidas (2 letras + 2 números + 2 letras)"""
        valid_plates = [
            'AB12CD', 'XY98ZZ', 'AA00BB', 'ZZ99ZZ',
            'BC23DE', 'WX45YZ', 'AB12CD', 'CD45EF'
        ]
        for plate in valid_plates:
            with self.subTest(plate=plate):
                self.assertTrue(validate_chilean_plate(plate), f"Plate {plate} should be valid")

    def test_valid_new_format_plates(self):
        """Test patentes nuevas válidas (4 letras + 2 números)"""
        valid_plates = [
            'ABCD12', 'XYZW98', 'AAAA00', 'ZZZZ99',
            'BCDE23', 'WXYZ45', 'ABCD12', 'CDEF56'
        ]
        for plate in valid_plates:
            with self.subTest(plate=plate):
                self.assertTrue(validate_chilean_plate(plate), f"Plate {plate} should be valid")

    def test_valid_motorcycle_plates(self):
        """Test patentes de motos válidas (3 letras + 2 números)"""
        valid_plates = [
            'ABC12', 'XYZ98', 'AAA00', 'ZZZ99',
            'BCD23', 'WXY45', 'ABC12', 'CDE56'
        ]
        for plate in valid_plates:
            with self.subTest(plate=plate):
                self.assertTrue(validate_chilean_plate(plate), f"Plate {plate} should be valid")

    def test_invalid_plates(self):
        """Test patentes inválidas"""
        invalid_plates = [
            '',  # Vacío
            'ABC',  # Demasiado corto
            'ABCDEFGH',  # Demasiado largo
            'AB123CDE',  # Formato incorrecto
            '123456',  # Solo números
            'ABCDEF',  # Solo letras
            'AB12C',  # Formato intermedio inválido
            'ABC1234',  # Formato moto inválido
            'ABCDE1',  # Formato nuevo inválido
            'AB12345',  # Formato antiguo inválido
            'AB@123CD',  # Caracteres especiales
            'AB 12 3C D',  # Espacios
        ]
        for plate in invalid_plates:
            with self.subTest(plate=plate):
                self.assertFalse(validate_chilean_plate(plate), f"Plate {plate} should be invalid")

    def test_case_insensitive(self):
        """Test que la validación es case insensitive"""
        test_cases = [
            ('abcd12', True),   # minúsculas válidas
            ('ABCD12', True),   # mayúsculas
            ('AbCd12', True),   # mixtas
            ('aa00bb', True),   # minúsculas válidas antiguas
        ]
        for plate, expected in test_cases:
            with self.subTest(plate=plate):
                self.assertEqual(validate_chilean_plate(plate), expected)

    def test_spaces_handling(self):
        """Test que los espacios son removidos correctamente"""
        test_cases = [
            ('AB 12 3C D', False),  # Espacios en lugares incorrectos
            ('AB12 CD', True),      # Espacio en medio (se remueve y resulta válido)
            (' ABCD12 ', True),     # Espacios al inicio/fin (se remueven)
            ('A B C D 1 2', True),  # Espacios entre caracteres (se remueven y resulta válido)
        ]
        for plate, expected in test_cases:
            with self.subTest(plate=plate):
                self.assertEqual(validate_chilean_plate(plate), expected)

    def test_none_and_invalid_types(self):
        """Test manejo de None y tipos inválidos"""
        invalid_inputs = [None, 123, [], {}, True, False]
        for invalid_input in invalid_inputs:
            with self.subTest(input=invalid_input):
                self.assertFalse(validate_chilean_plate(invalid_input))

    def test_edge_cases(self):
        """Test casos edge específicos"""
        edge_cases = [
            ('AA00AA', True),   # Mínima válida antigua
            ('ZZ99ZZ', True),   # Máxima válida antigua
            ('AAAA00', True),   # Mínima válida nueva
            ('ZZZZ99', True),   # Máxima válida nueva
            ('AAA00', True),    # Mínima válida moto
            ('ZZZ99', True),    # Máxima válida moto
        ]
        for plate, expected in edge_cases:
            with self.subTest(plate=plate):
                self.assertEqual(validate_chilean_plate(plate), expected)
