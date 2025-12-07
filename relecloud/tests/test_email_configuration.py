"""
Tests para verificar la configuración de Email SMTP
Siguiendo TDD - estos tests deben fallar inicialmente (fase ROJO)
"""
from django.test import TestCase
from django.conf import settings
from decouple import config
import os


class EmailConfigurationTest(TestCase):
    """
    Tests que verifican que las variables de entorno de EMAIL 
    están configuradas correctamente y que sean verificadas
    """
    
    def test_email_host_user_env_variable_exists(self):
        """
        Test: Verificar que la variable de entorno EMAIL_HOST_USER existe
        """
        try:
            email_user = config('EMAIL_HOST_USER')
            self.assertIsNotNone(
                email_user,
                "La variable de entorno EMAIL_HOST_USER no está configurada"
            )
        except Exception:
            self.fail("La variable de entorno EMAIL_HOST_USER no está configurada en .env")
    
    def test_email_host_password_env_variable_exists(self):
        """
        Test: Verificar que la variable de entorno EMAIL_HOST_PASSWORD existe
        """
        try:
            email_password = config('EMAIL_HOST_PASSWORD')
            self.assertIsNotNone(
                email_password,
                "La variable de entorno EMAIL_HOST_PASSWORD no está configurada"
            )
        except Exception:
            self.fail("La variable de entorno EMAIL_HOST_PASSWORD no está configurada en .env")
    
    def test_email_host_user_can_be_accessed_from_env(self):
        """
        Test: Verificar que EMAIL_HOST_USER se puede acceder desde las variables de entorno
        y tiene un valor válido
        """
        try:
            email_user = config('EMAIL_HOST_USER')
            self.assertIsNotNone(email_user)
            self.assertNotEqual(email_user, '')
            # Verificar formato de email
            self.assertIn('@', email_user)
            self.assertIn('gmail.com', email_user)
        except Exception as e:
            self.fail(f"No se pudo acceder a EMAIL_HOST_USER desde variables de entorno: {e}")
    
    def test_email_host_password_can_be_accessed_from_env(self):
        """
        Test: Verificar que EMAIL_HOST_PASSWORD se puede acceder desde las variables de entorno
        y tiene un valor válido
        """
        try:
            email_password = config('EMAIL_HOST_PASSWORD')
            self.assertIsNotNone(email_password)
            self.assertNotEqual(email_password, '')
            # La contraseña de aplicación de Gmail tiene un formato específico
            self.assertGreater(len(email_password), 10)
        except Exception as e:
            self.fail(f"No se pudo acceder a EMAIL_HOST_PASSWORD desde variables de entorno: {e}")
    
    def test_email_backend_configured_in_settings(self):
        """
        Test: Verificar que EMAIL_BACKEND está configurado en settings
        """
        self.assertTrue(
            hasattr(settings, 'EMAIL_BACKEND'),
            "EMAIL_BACKEND no está configurado en settings.py"
        )
        # En producción debe ser SMTP, en tests puede ser locmem
        self.assertIn(
            'EmailBackend',
            settings.EMAIL_BACKEND,
            "EMAIL_BACKEND no tiene un valor válido"
        )
    
    def test_email_host_configured_in_settings(self):
        """
        Test: Verificar que EMAIL_HOST está configurado para Gmail
        """
        self.assertTrue(
            hasattr(settings, 'EMAIL_HOST'),
            "EMAIL_HOST no está configurado en settings.py"
        )
        self.assertEqual(
            settings.EMAIL_HOST,
            'smtp.gmail.com',
            "EMAIL_HOST debe ser smtp.gmail.com"
        )
    
    def test_email_port_configured_in_settings(self):
        """
        Test: Verificar que EMAIL_PORT está configurado correctamente
        """
        self.assertTrue(
            hasattr(settings, 'EMAIL_PORT'),
            "EMAIL_PORT no está configurado en settings.py"
        )
        self.assertEqual(
            settings.EMAIL_PORT,
            587,
            "EMAIL_PORT debe ser 587 para TLS"
        )
    
    def test_email_use_tls_enabled_in_settings(self):
        """
        Test: Verificar que EMAIL_USE_TLS está habilitado
        """
        self.assertTrue(
            hasattr(settings, 'EMAIL_USE_TLS'),
            "EMAIL_USE_TLS no está configurado en settings.py"
        )
        self.assertTrue(
            settings.EMAIL_USE_TLS,
            "EMAIL_USE_TLS debe estar en True"
        )
    
    def test_notify_email_configured(self):
        """
        Test: Comprobar que NOTIFY_EMAIL está configurado
        Este será el email que recibe las notificaciones de InfoRequest
        """
        # Este test fallará inicialmente porque aún no existe NOTIFY_EMAIL en settings
        self.assertTrue(
            hasattr(settings, 'NOTIFY_EMAIL'),
            "NOTIFY_EMAIL no está configurado en settings.py"
        )
        self.assertIsNotNone(
            settings.NOTIFY_EMAIL,
            "NOTIFY_EMAIL no puede ser None"
        )
        self.assertNotEqual(
            settings.NOTIFY_EMAIL,
            '',
            "NOTIFY_EMAIL no puede estar vacío"
        )
        # Verificar que es un email válido
        self.assertIn('@', settings.NOTIFY_EMAIL)
    
    def test_default_from_email_configured(self):
        """
        Test: Verificar que DEFAULT_FROM_EMAIL está configurado
        """
        self.assertTrue(
            hasattr(settings, 'DEFAULT_FROM_EMAIL'),
            "DEFAULT_FROM_EMAIL no está configurado en settings.py"
        )
        self.assertIsNotNone(settings.DEFAULT_FROM_EMAIL)
        self.assertNotEqual(settings.DEFAULT_FROM_EMAIL, '')
