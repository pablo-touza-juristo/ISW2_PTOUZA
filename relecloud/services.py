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
    
    El correo se envía de forma síncrona durante el procesamiento de la solicitud.
    Si el envío falla, la función registra el error en los logs pero NO lanza
    excepciones, permitiendo que el procesamiento continúe normalmente.
    
    Comportamiento en caso de fallo:
        - El error se registra en los logs mediante logger.error()
        - Se retorna False para indicar el fallo
        - NO se lanza ninguna excepción (las excepciones se capturan internamente)
        - La solicitud en la base de datos NO se ve afectada
    
    Parameters:
        instance (InfoRequest): Instancia del modelo InfoRequest que contiene
                                los datos del formulario enviado por el usuario.
                                Debe tener los campos: name, email, cruise, notes
    
    Returns:
        bool: True si el correo se envió exitosamente, False en caso contrario.
              False puede indicar:
              - Error de conexión SMTP (SMTPException)
              - Error de autenticación SMTP
              - Configuración de correo incorrecta
              - Cualquier otro error durante el envío
    
    Posibles excepciones capturadas internamente:
        SMTPException: Errores relacionados con SMTP (conexión, autenticación, envío)
        Exception: Cualquier otra excepción no prevista durante el envío
        
    Nota:
        Esta función NO lanza excepciones. Todos los errores son capturados
        y registrados internamente, retornando False en caso de fallo.
    
    Example:
        >>> from relecloud.models import InfoRequest, Cruise
        >>> cruise = Cruise.objects.first()
        >>> info_request = InfoRequest.objects.create(
        ...     name='Juan Pérez',
        ...     email='juan@example.com',
        ...     cruise=cruise,
        ...     notes='Información sobre cruceros'
        ... )
        >>> success = send_info_request_email(info_request)
        >>> if success:
        ...     print("Correo enviado exitosamente")
        ... else:
        ...     print("Error al enviar correo, revisa los logs")
    """
    try:
        # Extraer datos de la instancia InfoRequest
        # Estos campos son validados por el modelo antes de llegar aquí
        nombre = instance.name
        email = instance.email
        mensaje = instance.notes
        
        # Construir el asunto del correo
        # Este asunto es consistente con los tests y la especificación del PBI
        asunto = 'Nueva solicitud de información'
        
        # Construir el cuerpo del correo con formato legible
        # Incluye toda la información necesaria para el administrador
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
        
        # Obtener configuración de correo desde settings.py
        # NOTIFY_EMAIL: destinatario (administrador)
        # DEFAULT_FROM_EMAIL: remitente (configurado con EMAIL_HOST_USER)
        email_destino = settings.NOTIFY_EMAIL
        email_remitente = settings.DEFAULT_FROM_EMAIL
        
        # Enviar el correo al administrador usando la función send_mail de Django
        # fail_silently=False: Lanza excepción si hay error (capturada por el try-except)
        send_mail(
            subject=asunto,
            message=cuerpo,
            from_email=email_remitente,
            recipient_list=[email_destino],
            fail_silently=False  # Lanzar excepción si falla para manejo explícito
        )
        
        # Enviar correo de confirmación al usuario
        asunto_confirmacion = 'Confirmación de solicitud de información - ReleCloud'
        cuerpo_confirmacion = f"""
Hola {nombre},

Gracias por contactar con ReleCloud. Hemos recibido tu solicitud de información correctamente.

Detalles de tu solicitud:
-------------------------
Crucero: {instance.cruise.name}
Mensaje enviado: {mensaje}

-------------------------
Nuestro equipo revisará tu solicitud y te responderemos a la brevedad posible a esta dirección de correo.

¡Gracias por confiar en ReleCloud para tu próxima aventura espacial!

Saludos,
El equipo de ReleCloud

-------------------------
Este es un mensaje automático, por favor no respondas a este correo.
        """
        
        # Enviar correo de confirmación al usuario
        send_mail(
            subject=asunto_confirmacion,
            message=cuerpo_confirmacion,
            from_email=email_remitente,
            recipient_list=[email],  # Enviar al email del usuario
            fail_silently=False
        )
        
        # Registrar el éxito en los logs para auditoría
        # Útil para verificar que las notificaciones se están enviando correctamente
        logger.info(
            f"Correos enviados exitosamente (admin + confirmación usuario). "
            f"Usuario: {nombre} ({email})"
        )
        
        return True
        
    except SMTPException as e:
        # Error específico de SMTP (conexión, autenticación, envío)
        # Estos errores suelen ser temporales o de configuración
        # Se registran con todos los detalles para facilitar el diagnóstico
        logger.error(
            f"Error SMTP al enviar correo de solicitud de información. "
            f"Usuario: {instance.name} ({instance.email}). "
            f"Error: {str(e)}"
        )
        # Retornar False para indicar fallo sin lanzar excepción
        # Esto permite que la vista maneje el error de forma controlada
        return False
        
    except Exception as e:
        # Cualquier otro error no previsto durante el envío
        # Puede incluir: configuración incorrecta, campos faltantes, etc.
        # Se registra el error completo para debugging
        logger.error(
            f"Error inesperado al enviar correo de solicitud de información. "
            f"Usuario: {instance.name} ({instance.email}). "
            f"Error: {str(e)}"
        )
        # Retornar False para indicar fallo
        # La instancia InfoRequest ya está guardada en la BD
        return False
