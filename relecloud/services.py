"""
Servicios de la aplicación ReleCloud
Incluye funcionalidades para envío de correos electrónicos
"""
import logging
from django.core.mail import send_mail
from django.conf import settings
from smtplib import SMTPException


# Configurar logger para este módulo
logger = logging.getLogger(__name__)


def send_info_request_email(instance):
    """
    Envía un correo de notificación cuando se recibe una nueva solicitud de información.
    
    Esta función extrae los datos de la instancia InfoRequest y envía un correo
    electrónico al administrador con la información proporcionada por el usuario.
    
    Parameters:
        instance (InfoRequest): Instancia del modelo InfoRequest que contiene
                                los datos del formulario enviado por el usuario.
                                Debe tener los campos: name, email, notes
    
    Returns:
        bool: True si el correo se envió exitosamente, False en caso contrario
    
    Raises:
        SMTPException: Si hay un error al conectar o enviar mediante SMTP
        Exception: Cualquier otra excepción no prevista durante el envío
    
    Example:
        >>> info_request = InfoRequest.objects.create(
        ...     name='Juan Pérez',
        ...     email='juan@example.com',
        ...     notes='Información sobre cruceros'
        ... )
        >>> send_info_request_email(info_request)
        True
    """
    try:
        # Extraer datos de la instancia
        nombre = instance.name
        email = instance.email
        mensaje = instance.notes
        
        # Construir el asunto del correo
        asunto = 'Nueva solicitud de información'
        
        # Construir el cuerpo del correo
        cuerpo = f"""
Has recibido una nueva solicitud de información desde el sitio web de ReleCloud.

Detalles de la solicitud:
-------------------------
Nombre: {nombre}
Email: {email}

Mensaje:
{mensaje}

-------------------------
Este es un mensaje automático generado por el sistema ReleCloud.
        """
        
        # Obtener el email de notificación desde la configuración
        email_destino = settings.NOTIFY_EMAIL
        email_remitente = settings.DEFAULT_FROM_EMAIL
        
        # Enviar el correo
        send_mail(
            subject=asunto,
            message=cuerpo,
            from_email=email_remitente,
            recipient_list=[email_destino],
            fail_silently=False  # Lanzar excepción si falla
        )
        
        # Log de éxito
        logger.info(
            f"Correo de solicitud de información enviado exitosamente. "
            f"Usuario: {nombre} ({email})"
        )
        
        return True
        
    except SMTPException as e:
        # Error específico de SMTP
        logger.error(
            f"Error SMTP al enviar correo de solicitud de información. "
            f"Usuario: {instance.name} ({instance.email}). "
            f"Error: {str(e)}"
        )
        return False
        
    except Exception as e:
        # Cualquier otro error no previsto
        logger.error(
            f"Error inesperado al enviar correo de solicitud de información. "
            f"Usuario: {instance.name} ({instance.email}). "
            f"Error: {str(e)}"
        )
        return False
