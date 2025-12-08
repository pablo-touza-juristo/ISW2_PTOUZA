"""
Tests para verificar la conexión y envío de emails mediante SMTP
Siguiendo TDD - estos tests deben fallar inicialmente (fase ROJO)
"""
from django.test import TestCase
from django.core.mail import send_mail
from django.conf import settings
import smtplib
import socket


class EmailConnectionTest(TestCase):
    """
    Tests que verifican la conexión al servidor SMTP
    y la capacidad de enviar correos
    """
    
    def test_smtp_server_is_reachable(self):
        """
        Test: Verificar que el servidor SMTP de Gmail es alcanzable
        """
        try:
            # Intentar conectar al servidor SMTP
            with socket.create_connection((settings.EMAIL_HOST, settings.EMAIL_PORT), timeout=10):
                pass  # Si llegamos aquí, la conexión fue exitosa
        except (socket.timeout, socket.error) as e:
            self.fail(f"No se pudo conectar al servidor SMTP {settings.EMAIL_HOST}:{settings.EMAIL_PORT}. Error: {e}")
    
    def test_smtp_authentication_works(self):
        """
        Test: Verificar que las credenciales SMTP son válidas y la autenticación funciona
        """
        try:
            # Crear conexión SMTP
            smtp = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT, timeout=10)
            smtp.starttls()  # Iniciar TLS
            
            # Intentar autenticación
            smtp.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            smtp.quit()
            
        except smtplib.SMTPAuthenticationError as e:
            self.fail(f"Error de autenticación SMTP. Verifica EMAIL_HOST_USER y EMAIL_HOST_PASSWORD. Error: {e}")
        except smtplib.SMTPException as e:
            self.fail(f"Error en conexión SMTP: {e}")
        except Exception as e:
            self.fail(f"Error inesperado al conectar con SMTP: {e}")
    
    def test_can_send_test_email(self):
        """
        Test: Verificar que se puede enviar un correo de prueba
        """
        try:
            # Intentar enviar un correo de prueba
            num_sent = send_mail(
                subject='Test Email from ReleCloud',
                message='This is a test email from the ReleCloud application to verify SMTP configuration.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.NOTIFY_EMAIL],
                fail_silently=False,
            )
            
            # Verificar que se envió al menos 1 correo
            self.assertEqual(
                num_sent,
                1,
                "No se pudo enviar el correo de prueba"
            )
            
        except Exception as e:
            self.fail(f"Error al enviar correo de prueba: {e}")
    
    def test_at_least_one_email_sent(self):
        """
        Test: Verificar que al menos se ha enviado 1 correo
        Este test verifica el resultado del envío anterior
        """
        # Enviar un correo
        send_mail(
            subject='Test Email - Verification',
            message='Verifying that at least one email has been sent.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.NOTIFY_EMAIL],
            fail_silently=False,
        )
        
        # En entorno de test, Django usa el backend 'locmem'
        # que almacena los emails en memoria
        from django.core import mail
        
        # Verificar que hay al menos 1 email en la bandeja de salida
        self.assertGreaterEqual(
            len(mail.outbox),
            1,
            "No se ha enviado ningún correo"
        )
    
    def test_email_content_is_correct(self):
        """
        Test: Verificar que el contenido del correo enviado es correcto
        """
        subject = 'Test Subject'
        message = 'Test Message Body'
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient = settings.NOTIFY_EMAIL
        
        # Enviar correo
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=[recipient],
            fail_silently=False,
        )
        
        # Verificar el contenido del último email enviado
        from django.core import mail
        
        self.assertGreater(len(mail.outbox), 0, "No hay correos en la bandeja de salida")
        
        last_email = mail.outbox[-1]
        
        self.assertEqual(last_email.subject, subject)
        self.assertEqual(last_email.body, message)
        self.assertEqual(last_email.from_email, from_email)
        self.assertIn(recipient, last_email.to)
