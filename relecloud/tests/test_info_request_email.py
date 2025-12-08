"""
Tests para verificar el envío de correo desde el formulario info_request
Siguiendo TDD - estos tests deben fallar inicialmente (fase ROJO)
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.core import mail
from relecloud.models import InfoRequest, Usuario, Cruise, Destination


class InfoRequestEmailTest(TestCase):
    """
    Tests que verifican el envío de correo cuando un usuario
    envía el formulario de solicitud de información
    """
    
    def setUp(self):
        """
        Configuración inicial para cada test
        """
        self.client = Client()
        self.url = reverse('info_request')
        
        # Crear un usuario de prueba (requerido por LoginRequiredMixin)
        self.user = Usuario.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        # Autenticar al usuario
        self.client.login(username='testuser', password='testpass123')
        
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
        
        # Datos válidos para el formulario
        self.valid_data = {
            'name': 'Juan Pérez',
            'email': 'juan.perez@example.com',
            'cruise': self.cruise.id,
            'notes': 'Estoy interesado en el crucero a Marte. ¿Podrían enviarme más información sobre fechas y precios?'
        }
    
    def test_email_sent_when_form_submitted_with_valid_data(self):
        """
        Test: Verificar que se envía exactamente 1 correo cuando el formulario
        se envía con datos válidos mediante método HTTP POST
        """
        # Limpiar la bandeja de salida antes del test
        mail.outbox = []
        
        # Enviar formulario con datos válidos
        response = self.client.post(self.url, self.valid_data)
        
        # Verificar que se envió exactamente 1 correo
        self.assertEqual(
            len(mail.outbox),
            1,
            "Debe enviarse exactamente 1 correo cuando se envía el formulario con datos válidos"
        )
    
    def test_email_subject_is_correct(self):
        """
        Test: Verificar que el asunto del correo es "Nueva solicitud de información"
        """
        # Limpiar la bandeja de salida
        mail.outbox = []
        
        # Enviar formulario
        response = self.client.post(self.url, self.valid_data)
        
        # Verificar que hay al menos un correo
        self.assertGreater(len(mail.outbox), 0, "Debe haber al menos un correo enviado")
        
        # Verificar el asunto
        sent_email = mail.outbox[0]
        self.assertEqual(
            sent_email.subject,
            'Nueva solicitud de información',
            "El asunto del correo debe ser 'Nueva solicitud de información'"
        )
    
    def test_email_body_contains_user_name(self):
        """
        Test: Verificar que el cuerpo del correo contiene el nombre del usuario
        """
        # Limpiar la bandeja de salida
        mail.outbox = []
        
        # Enviar formulario
        response = self.client.post(self.url, self.valid_data)
        
        # Verificar que hay al menos un correo
        self.assertGreater(len(mail.outbox), 0, "Debe haber al menos un correo enviado")
        
        # Verificar que el cuerpo contiene el nombre del usuario
        sent_email = mail.outbox[0]
        self.assertIn(
            self.valid_data['name'],
            sent_email.body,
            f"El cuerpo del correo debe contener el nombre del usuario: {self.valid_data['name']}"
        )
    
    def test_email_body_contains_user_email(self):
        """
        Test: Verificar que el cuerpo del correo contiene el email del usuario
        """
        # Limpiar la bandeja de salida
        mail.outbox = []
        
        # Enviar formulario
        response = self.client.post(self.url, self.valid_data)
        
        # Verificar que hay al menos un correo
        self.assertGreater(len(mail.outbox), 0, "Debe haber al menos un correo enviado")
        
        # Verificar que el cuerpo contiene el email del usuario
        sent_email = mail.outbox[0]
        self.assertIn(
            self.valid_data['email'],
            sent_email.body,
            f"El cuerpo del correo debe contener el email del usuario: {self.valid_data['email']}"
        )
    
    def test_email_body_contains_user_message(self):
        """
        Test: Verificar que el cuerpo del correo contiene el mensaje del usuario
        """
        # Limpiar la bandeja de salida
        mail.outbox = []
        
        # Enviar formulario
        response = self.client.post(self.url, self.valid_data)
        
        # Verificar que hay al menos un correo
        self.assertGreater(len(mail.outbox), 0, "Debe haber al menos un correo enviado")
        
        # Verificar que el cuerpo contiene el mensaje del usuario
        sent_email = mail.outbox[0]
        self.assertIn(
            self.valid_data['notes'],
            sent_email.body,
            "El cuerpo del correo debe contener el mensaje del usuario"
        )
    
    def test_no_email_sent_with_invalid_data(self):
        """
        Test: Verificar que NO se envía correo cuando el formulario
        tiene datos inválidos
        """
        # Limpiar la bandeja de salida
        mail.outbox = []
        
        # Datos inválidos (email sin formato correcto)
        invalid_data = {
            'name': 'Juan Pérez',
            'email': 'email-invalido',
            'notes': 'Mensaje de prueba'
        }
        
        # Enviar formulario con datos inválidos
        response = self.client.post(self.url, invalid_data)
        
        # Verificar que NO se envió ningún correo
        self.assertEqual(
            len(mail.outbox),
            0,
            "NO debe enviarse ningún correo cuando los datos son inválidos"
        )
    
    def test_form_saves_to_database_when_valid(self):
        """
        Test: Verificar que el formulario se guarda en la base de datos
        cuando los datos son válidos
        """
        # Contar registros antes
        count_before = InfoRequest.objects.count()
        
        # Enviar formulario
        response = self.client.post(self.url, self.valid_data)
        
        # Contar registros después
        count_after = InfoRequest.objects.count()
        
        # Verificar que se creó un nuevo registro
        self.assertEqual(
            count_after,
            count_before + 1,
            "Debe crearse un nuevo registro en la base de datos cuando el formulario es válido"
        )
