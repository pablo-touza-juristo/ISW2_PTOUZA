"""
Comando de gestión de Django para probar la conexión SMTP
y enviar un correo de prueba.

Uso:
    python manage.py test_smtp_connection
"""
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
import smtplib
import socket


class Command(BaseCommand):
    help = 'Prueba la conexión SMTP y envía un correo de prueba para verificar la configuración'

    def handle(self, *args, **options):
        """
        Método principal que ejecuta el comando
        """
        self.stdout.write(self.style.HTTP_INFO('=== Prueba de Conexión SMTP ===\n'))
        
        # 1. Verificar configuración
        self.stdout.write('📋 Verificando configuración...')
        self._check_configuration()
        
        # 2. Probar conectividad al servidor
        self.stdout.write('\n🔌 Probando conectividad al servidor SMTP...')
        self._test_server_connectivity()
        
        # 3. Probar autenticación
        self.stdout.write('\n🔐 Probando autenticación SMTP...')
        self._test_authentication()
        
        # 4. Enviar correo de prueba
        self.stdout.write('\n📧 Enviando correo de prueba...')
        self._send_test_email()
        
        # Mensaje final
        self.stdout.write(self.style.SUCCESS('\n✅ ¡Todas las pruebas completadas exitosamente!'))
        self.stdout.write(self.style.SUCCESS(f'   Correo enviado a: {settings.NOTIFY_EMAIL}\n'))

    def _check_configuration(self):
        """
        Verifica que todas las variables de configuración estén definidas
        """
        try:
            self.stdout.write(f'   EMAIL_BACKEND: {settings.EMAIL_BACKEND}')
            self.stdout.write(f'   EMAIL_HOST: {settings.EMAIL_HOST}')
            self.stdout.write(f'   EMAIL_PORT: {settings.EMAIL_PORT}')
            self.stdout.write(f'   EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}')
            self.stdout.write(f'   EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}')
            self.stdout.write(f'   EMAIL_HOST_PASSWORD: {"*" * len(settings.EMAIL_HOST_PASSWORD)}')
            self.stdout.write(f'   DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}')
            self.stdout.write(f'   NOTIFY_EMAIL: {settings.NOTIFY_EMAIL}')
            
            self.stdout.write(self.style.SUCCESS('   ✓ Configuración verificada'))
            
        except AttributeError as e:
            self.stdout.write(self.style.ERROR(f'   ✗ Error: Falta configuración - {e}'))
            raise

    def _test_server_connectivity(self):
        """
        Prueba la conectividad con el servidor SMTP
        """
        try:
            with socket.create_connection(
                (settings.EMAIL_HOST, settings.EMAIL_PORT),
                timeout=10
            ):
                self.stdout.write(self.style.SUCCESS(
                    f'   ✓ Servidor {settings.EMAIL_HOST}:{settings.EMAIL_PORT} es alcanzable'
                ))
        except (socket.timeout, socket.error) as e:
            self.stdout.write(self.style.ERROR(
                f'   ✗ Error: No se pudo conectar al servidor SMTP - {e}'
            ))
            raise

    def _test_authentication(self):
        """
        Prueba la autenticación con el servidor SMTP
        """
        try:
            smtp = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT, timeout=10)
            smtp.starttls()
            smtp.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            smtp.quit()
            
            self.stdout.write(self.style.SUCCESS(
                '   ✓ Autenticación SMTP exitosa'
            ))
            
        except smtplib.SMTPAuthenticationError as e:
            self.stdout.write(self.style.ERROR(
                f'   ✗ Error de autenticación: Verifica las credenciales - {e}'
            ))
            raise
        except smtplib.SMTPException as e:
            self.stdout.write(self.style.ERROR(
                f'   ✗ Error SMTP: {e}'
            ))
            raise

    def _send_test_email(self):
        """
        Envía un correo de prueba
        """
        try:
            subject = 'Test Email from ReleCloud - SMTP Configuration'
            message = """
Hola,

Este es un correo de prueba enviado desde la aplicación ReleCloud para verificar 
que la configuración SMTP está funcionando correctamente.

Si recibes este mensaje, significa que:
✓ La conexión al servidor SMTP es exitosa
✓ Las credenciales de autenticación son correctas
✓ El envío de correos está funcionando

Detalles técnicos:
- Servidor SMTP: {host}
- Puerto: {port}
- TLS: {tls}
- Desde: {from_email}

Saludos,
Sistema ReleCloud
            """.format(
                host=settings.EMAIL_HOST,
                port=settings.EMAIL_PORT,
                tls='Habilitado' if settings.EMAIL_USE_TLS else 'Deshabilitado',
                from_email=settings.DEFAULT_FROM_EMAIL
            )
            
            num_sent = send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.NOTIFY_EMAIL],
                fail_silently=False,
            )
            
            if num_sent == 1:
                self.stdout.write(self.style.SUCCESS(
                    '   ✓ Correo de prueba enviado exitosamente'
                ))
            else:
                self.stdout.write(self.style.WARNING(
                    f'   ⚠ Se esperaba enviar 1 correo, pero se enviaron {num_sent}'
                ))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f'   ✗ Error al enviar correo: {e}'
            ))
            raise
