"""
Tests de validación del modelo InfoRequest
Siguiendo TDD - estos tests deben fallar inicialmente (fase ROJO)
"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from relecloud.models import InfoRequest, Cruise, Destination


class InfoRequestValidationTest(TestCase):
    """
    Tests que verifican las validaciones del modelo InfoRequest
    para asegurar que se rechazan datos inválidos y se muestran
    mensajes de error apropiados
    """
    
    def setUp(self):
        """
        Configuración inicial para cada test
        """
        # Crear un destino de prueba
        self.destination = Destination.objects.create(
            name='Marte',
            description='El planeta rojo'
        )
        
        # Crear un crucero de prueba
        self.cruise = Cruise.objects.create(
            name='Viaje a Marte',
            description='Un increíble viaje al planeta rojo'
        )
        self.cruise.destinations.add(self.destination)
        
        # Datos válidos para comparación
        self.valid_data = {
            'name': 'Juan Pérez',
            'email': 'juan.perez@example.com',
            'cruise': self.cruise,
            'notes': 'Estoy interesado en el crucero a Marte.'
        }
    
    def test_name_field_cannot_be_blank(self):
        """
        Test: Verificar que el campo 'name' no puede estar vacío
        El sistema debe rechazar una solicitud sin nombre
        """
        info_request = InfoRequest(
            name='',  # Campo vacío
            email='juan@example.com',
            cruise=self.cruise,
            notes='Mensaje de prueba'
        )
        
        # Verificar que full_clean() lanza ValidationError
        with self.assertRaises(ValidationError) as context:
            info_request.full_clean()
        
        # Verificar que el error está en el campo 'name'
        self.assertIn('name', context.exception.error_dict)
        
        # Verificar que el mensaje de error sea apropiado
        error_messages = [str(error) for error in context.exception.error_dict['name']]
        self.assertTrue(
            any('nombre' in msg.lower() for msg in error_messages),
            f"El mensaje de error debe mencionar el nombre. Mensajes recibidos: {error_messages}"
        )
    
    def test_email_field_validates_format(self):
        """
        Test: Verificar que el campo 'email' valida el formato de correo electrónico
        El sistema debe rechazar emails con formato inválido
        """
        invalid_emails = [
            'email-sin-arroba',
            'email@',
            '@dominio.com',
            'email@dominio',
            'email con espacios@dominio.com'
        ]
        
        for invalid_email in invalid_emails:
            with self.subTest(email=invalid_email):
                info_request = InfoRequest(
                    name='Juan Pérez',
                    email=invalid_email,
                    cruise=self.cruise,
                    notes='Mensaje de prueba'
                )
                
                # Verificar que full_clean() lanza ValidationError
                with self.assertRaises(ValidationError) as context:
                    info_request.full_clean()
                
                # Verificar que el error está en el campo 'email'
                self.assertIn('email', context.exception.error_dict,
                             f"Debe rechazar el email inválido: {invalid_email}")
    
    def test_email_field_accepts_valid_format(self):
        """
        Test: Verificar que el campo 'email' acepta formatos válidos
        """
        valid_emails = [
            'usuario@ejemplo.com',
            'nombre.apellido@dominio.es',
            'usuario+tag@empresa.co.uk'
        ]
        
        for valid_email in valid_emails:
            with self.subTest(email=valid_email):
                info_request = InfoRequest(
                    name='Juan Pérez',
                    email=valid_email,
                    cruise=self.cruise,
                    notes='Mensaje de prueba'
                )
                
                # No debe lanzar excepción con email válido
                try:
                    info_request.full_clean()
                    info_request.save()
                except ValidationError:
                    self.fail(f"El email válido '{valid_email}' fue rechazado incorrectamente")
    
    def test_notes_field_cannot_be_blank(self):
        """
        Test: Verificar que el campo 'notes' no puede estar vacío
        El usuario debe proporcionar un mensaje
        """
        info_request = InfoRequest(
            name='Juan Pérez',
            email='juan@example.com',
            cruise=self.cruise,
            notes=''  # Campo vacío
        )
        
        # Verificar que full_clean() lanza ValidationError
        with self.assertRaises(ValidationError) as context:
            info_request.full_clean()
        
        # Verificar que el error está en el campo 'notes'
        self.assertIn('notes', context.exception.error_dict)
    
    def test_name_field_max_length_validation(self):
        """
        Test: Verificar que el campo 'name' respeta el max_length de 50 caracteres
        """
        # Crear un nombre de más de 50 caracteres
        long_name = 'A' * 51
        
        info_request = InfoRequest(
            name=long_name,
            email='juan@example.com',
            cruise=self.cruise,
            notes='Mensaje de prueba'
        )
        
        # Verificar que full_clean() lanza ValidationError
        with self.assertRaises(ValidationError) as context:
            info_request.full_clean()
        
        # Verificar que el error está en el campo 'name'
        self.assertIn('name', context.exception.error_dict)
        
        # Verificar que el mensaje menciona el límite de caracteres
        error_messages = [str(error) for error in context.exception.error_dict['name']]
        self.assertTrue(
            any('50' in msg for msg in error_messages),
            f"El mensaje debe indicar el límite de 50 caracteres. Mensajes: {error_messages}"
        )
    
    def test_notes_field_max_length_validation(self):
        """
        Test: Verificar que el campo 'notes' respeta el max_length de 2000 caracteres
        """
        # Crear notas de más de 2000 caracteres
        long_notes = 'A' * 2001
        
        info_request = InfoRequest(
            name='Juan Pérez',
            email='juan@example.com',
            cruise=self.cruise,
            notes=long_notes
        )
        
        # Verificar que full_clean() lanza ValidationError
        with self.assertRaises(ValidationError) as context:
            info_request.full_clean()
        
        # Verificar que el error está en el campo 'notes'
        self.assertIn('notes', context.exception.error_dict)
        
        # Verificar que el mensaje menciona el límite de caracteres
        error_messages = [str(error) for error in context.exception.error_dict['notes']]
        self.assertTrue(
            any('2000' in msg for msg in error_messages),
            f"El mensaje debe indicar el límite de 2000 caracteres. Mensajes: {error_messages}"
        )
    
    def test_cruise_field_is_required(self):
        """
        Test: Verificar que el campo 'cruise' es obligatorio
        """
        info_request = InfoRequest(
            name='Juan Pérez',
            email='juan@example.com',
            cruise=None,  # Sin crucero
            notes='Mensaje de prueba'
        )
        
        # Verificar que full_clean() lanza ValidationError
        with self.assertRaises(ValidationError) as context:
            info_request.full_clean()
        
        # Verificar que el error está en el campo 'cruise'
        self.assertIn('cruise', context.exception.error_dict)
    
    def test_valid_info_request_saves_successfully(self):
        """
        Test: Verificar que una solicitud con datos válidos se guarda correctamente
        """
        info_request = InfoRequest(**self.valid_data)
        
        # No debe lanzar excepción
        try:
            info_request.full_clean()
            info_request.save()
        except ValidationError as e:
            self.fail(f"Una solicitud válida no debería lanzar ValidationError: {e}")
        
        # Verificar que se guardó en la base de datos
        self.assertIsNotNone(info_request.id)
        self.assertEqual(InfoRequest.objects.count(), 1)
    
    def test_error_messages_are_user_friendly(self):
        """
        Test: Verificar que los mensajes de error son claros y orientan al usuario
        Este test verifica que los mensajes personalizados se muestran correctamente
        """
        # Test con nombre vacío
        info_request = InfoRequest(
            name='',
            email='email-invalido',
            cruise=self.cruise,
            notes=''
        )
        
        with self.assertRaises(ValidationError) as context:
            info_request.full_clean()
        
        # Verificar que hay errores
        self.assertTrue(len(context.exception.error_dict) > 0)
        
        # Los mensajes de error deben existir para los campos inválidos
        self.assertIn('name', context.exception.error_dict)
        self.assertIn('email', context.exception.error_dict)
        self.assertIn('notes', context.exception.error_dict)
