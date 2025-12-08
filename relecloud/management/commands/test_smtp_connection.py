"""
Comando de gestión de Django para probar la conexión SMTP
y enviar un correo de prueba.

Uso:
    python manage.py test_smtp_connection

Este comando verifica:
- Configuración de variables de entorno
- Conectividad al servidor SMTP
- Autenticación con credenciales
- Envío de correo de prueba

Incluye logging detallado para trazabilidad.
"""
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
import smtplib
import socket
import logging

# Configurar logger para el comando
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Prueba la conexión SMTP y envía un correo de prueba para verificar la configuración'

    def handle(self, *args, **options):
        """
        Método principal que ejecuta el comando
        """
        # Header con estilo
        self.stdout.write(self.style.HTTP_INFO('=' * 60))
        self.stdout.write(self.style.HTTP_INFO('    PRUEBA DE CONEXIÓN SMTP - RELECLOUD'))
        self.stdout.write(self.style.HTTP_INFO('=' * 60))
        self.stdout.write('')
        
        logger.info('Iniciando prueba de conexión SMTP')
        
        # 1. Verificar configuración
        self.stdout.write(self.style.HTTP_INFO('📋 PASO 1: Verificación de Configuración'))
        self.stdout.write(self.style.HTTP_INFO('-' * 60))
        if not self._check_configuration():
            logger.error('Error en verificación de configuración')
            return
        
        # 2. Probar conectividad al servidor
        self.stdout.write('')
        self.stdout.write(self.style.HTTP_INFO('🔌 PASO 2: Prueba de Conectividad'))
        self.stdout.write(self.style.HTTP_INFO('-' * 60))
        if not self._test_server_connectivity():
            logger.error('Error en conectividad al servidor')
            return
        
        # 3. Probar autenticación
        self.stdout.write('')
        self.stdout.write(self.style.HTTP_INFO('🔐 PASO 3: Prueba de Autenticación'))
        self.stdout.write(self.style.HTTP_INFO('-' * 60))
        if not self._test_authentication():
            logger.error('Error en autenticación SMTP')
            return
        
        # 4. Enviar correo de prueba
        self.stdout.write('')
        self.stdout.write(self.style.HTTP_INFO('📧 PASO 4: Envío de Correo de Prueba'))
        self.stdout.write(self.style.HTTP_INFO('-' * 60))
        if not self._send_test_email():
            logger.error('Error al enviar correo de prueba')
            return
        
        # Mensaje final de éxito
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('✅ ¡TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE!'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS(f'   📬 Correo enviado a: {settings.NOTIFY_EMAIL}'))
        self.stdout.write(self.style.SUCCESS(f'   📊 Configuración SMTP verificada correctamente'))
        self.stdout.write('')
        
        logger.info('Prueba de conexión SMTP completada exitosamente')

    def _check_configuration(self):
        """
        Verifica que todas las variables de configuración estén definidas
        Returns: True si la configuración es válida, False en caso contrario
        """
        try:
            # Verificar cada configuración con detalles
            config_items = [
                ('EMAIL_BACKEND', settings.EMAIL_BACKEND, 'Backend de email'),
                ('EMAIL_HOST', settings.EMAIL_HOST, 'Servidor SMTP'),
                ('EMAIL_PORT', settings.EMAIL_PORT, 'Puerto SMTP'),
                ('EMAIL_USE_TLS', settings.EMAIL_USE_TLS, 'TLS habilitado'),
                ('EMAIL_HOST_USER', settings.EMAIL_HOST_USER, 'Usuario SMTP'),
                ('EMAIL_HOST_PASSWORD', '*' * 20, 'Contraseña SMTP (oculta)'),
                ('DEFAULT_FROM_EMAIL', settings.DEFAULT_FROM_EMAIL, 'Email remitente'),
                ('NOTIFY_EMAIL', settings.NOTIFY_EMAIL, 'Email de notificación'),
            ]
            
            for key, value, description in config_items:
                if key == 'EMAIL_HOST_PASSWORD':
                    self.stdout.write(f'   {description:.<40} {self.style.WARNING(value)}')
                else:
                    self.stdout.write(f'   {description:.<40} {self.style.SUCCESS(str(value))}')
            
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('   ✓ Todas las variables de configuración están definidas'))
            
            logger.info(f'Configuración verificada: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}')
            return True
            
        except AttributeError as e:
            self.stdout.write(self.style.ERROR(f'   ✗ Error: Falta configuración - {e}'))
            logger.error(f'Configuración incompleta: {e}')
            return False

    def _test_server_connectivity(self):
        """
        Prueba la conectividad con el servidor SMTP
        Returns: True si la conexión es exitosa, False en caso contrario
        """
        try:
            self.stdout.write(f'   Intentando conectar a {settings.EMAIL_HOST}:{settings.EMAIL_PORT}...')
            
            with socket.create_connection(
                (settings.EMAIL_HOST, settings.EMAIL_PORT),
                timeout=10
            ):
                self.stdout.write(self.style.SUCCESS(
                    f'   ✓ Conexión establecida exitosamente'
                ))
                self.stdout.write(f'   ℹ️  Servidor: {settings.EMAIL_HOST}')
                self.stdout.write(f'   ℹ️  Puerto: {settings.EMAIL_PORT}')
                
            logger.info(f'Conectividad exitosa a {settings.EMAIL_HOST}:{settings.EMAIL_PORT}')
            return True
            
        except socket.timeout:
            self.stdout.write(self.style.ERROR(
                f'   ✗ Error: Timeout al conectar con el servidor'
            ))
            self.stdout.write(self.style.ERROR(
                f'   ℹ️  El servidor {settings.EMAIL_HOST} no responde'
            ))
            logger.error(f'Timeout en conexión a {settings.EMAIL_HOST}')
            return False
            
        except socket.error as e:
            self.stdout.write(self.style.ERROR(
                f'   ✗ Error de conexión: {e}'
            ))
            logger.error(f'Error de socket al conectar: {e}')
            return False

    def _test_authentication(self):
        """
        Prueba la autenticación con el servidor SMTP
        Returns: True si la autenticación es exitosa, False en caso contrario
        """
        try:
            self.stdout.write(f'   Estableciendo conexión SMTP...')
            smtp = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT, timeout=10)
            
            self.stdout.write(f'   Iniciando TLS...')
            smtp.starttls()
            
            self.stdout.write(f'   Autenticando con {settings.EMAIL_HOST_USER}...')
            smtp.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            smtp.quit()
            
            self.stdout.write(self.style.SUCCESS(
                '   ✓ Autenticación SMTP exitosa'
            ))
            self.stdout.write(f'   ℹ️  Usuario: {settings.EMAIL_HOST_USER}')
            
            logger.info(f'Autenticación exitosa con usuario {settings.EMAIL_HOST_USER}')
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            self.stdout.write(self.style.ERROR(
                f'   ✗ Error de autenticación'
            ))
            self.stdout.write(self.style.ERROR(
                f'   ℹ️  Verifica EMAIL_HOST_USER y EMAIL_HOST_PASSWORD'
            ))
            self.stdout.write(self.style.ERROR(f'   Detalle: {e}'))
            logger.error(f'Error de autenticación SMTP: {e}')
            return False
            
        except smtplib.SMTPException as e:
            self.stdout.write(self.style.ERROR(
                f'   ✗ Error SMTP: {e}'
            ))
            logger.error(f'Excepción SMTP: {e}')
            return False
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f'   ✗ Error inesperado: {e}'
            ))
            logger.error(f'Error inesperado en autenticación: {e}')
            return False

    def _send_test_email(self):
        """
        Envía un correo de prueba
        Returns: True si el envío es exitoso, False en caso contrario
        """
        try:
            subject = '✅ Test Email from ReleCloud - SMTP Configuration Verified'
            message = """
¡Hola!

Este es un correo de prueba enviado desde la aplicación ReleCloud para verificar 
que la configuración SMTP está funcionando correctamente.

Si recibes este mensaje, significa que:
✓ La conexión al servidor SMTP es exitosa
✓ Las credenciales de autenticación son correctas
✓ El envío de correos está funcionando perfectamente

═══════════════════════════════════════════════════════════
DETALLES TÉCNICOS DE LA CONFIGURACIÓN
═══════════════════════════════════════════════════════════

Servidor SMTP:      {host}
Puerto:             {port}
Seguridad TLS:      {tls}
Email remitente:    {from_email}
Email destino:      {to_email}

═══════════════════════════════════════════════════════════

Saludos,
Sistema ReleCloud 🚀
            """.format(
                host=settings.EMAIL_HOST,
                port=settings.EMAIL_PORT,
                tls='✓ Habilitado' if settings.EMAIL_USE_TLS else '✗ Deshabilitado',
                from_email=settings.DEFAULT_FROM_EMAIL,
                to_email=settings.NOTIFY_EMAIL
            )
            
            self.stdout.write(f'   Preparando correo de prueba...')
            self.stdout.write(f'   De: {settings.DEFAULT_FROM_EMAIL}')
            self.stdout.write(f'   Para: {settings.NOTIFY_EMAIL}')
            self.stdout.write(f'   Asunto: {subject}')
            self.stdout.write('')
            self.stdout.write(f'   Enviando...')
            
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
                self.stdout.write(self.style.SUCCESS(
                    f'   ℹ️  Revisa la bandeja de entrada de {settings.NOTIFY_EMAIL}'
                ))
                logger.info(f'Correo de prueba enviado a {settings.NOTIFY_EMAIL}')
                return True
            else:
                self.stdout.write(self.style.WARNING(
                    f'   ⚠ Advertencia: Se esperaba enviar 1 correo, pero se enviaron {num_sent}'
                ))
                logger.warning(f'Número de correos enviados: {num_sent} (esperado: 1)')
                return num_sent > 0
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f'   ✗ Error al enviar correo: {e}'
            ))
            logger.error(f'Error al enviar correo de prueba: {e}')
            return False
