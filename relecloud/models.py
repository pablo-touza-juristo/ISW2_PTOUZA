from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.
class Usuario(AbstractUser):
    """
    Modelo de usuario personalizado para ReleCloud
    """
    # AbstractUser ya incluye: username, first_name, last_name, email, password
    # Hacemos que email sea obligatorio
    email = models.EmailField(
        unique=True,
        null=False,
        blank=False,
    )
    telefono = models.CharField(
        max_length=20,
        null=True,
        blank=True,
    )
    
    # Campos obligatorios para registro
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
    
    def __str__(self):
        return f"{self.username} - {self.get_full_name()}"

class Destination(models.Model):
    name = models.CharField(
        unique=True,
        max_length=50,
        null=False,
        blank=False,
    )
    description = models.TextField(
        max_length=2000,
        null=False,
        blank=False
    )
    image = models.ImageField(
        upload_to='destinations/',
        null=True,
        blank=True,
        help_text='Imagen del destino (opcional)'
    )
    
    @property
    def image_url(self):
        """Retorna la URL de la imagen del destino o un placeholder si no existe"""
        try:
            if self.image and hasattr(self.image, 'url'):
                return self.image.url
        except (ValueError, AttributeError):
            # Si hay algún error al acceder a la imagen, usar placeholder
            pass
        # Placeholder por defecto si no hay imagen
        return 'https://via.placeholder.com/400x300?text=No+Image'
    
    def __str__(self):
        return self.name
    
    def get_average_rating(self):
        """Retorna la calificación promedio del destino"""
        from django.db.models import Avg
        result = self.reviews.aggregate(Avg('rating'))
        avg = result['rating__avg']
        return round(avg, 1) if avg is not None else None
    
    def get_review_count(self):
        """Retorna el número total de reviews"""
        return self.reviews.count()
    
    def get_rating_distribution(self):
        """Retorna la distribución de calificaciones"""
        from django.db.models import Count
        return self.reviews.values('rating').annotate(count=Count('rating')).order_by('-rating')

class Cruise(models.Model):
    name = models.CharField(
        unique=True,
        max_length=50,
        null=False,
        blank=False,
    )
    description = models.TextField(
        max_length=2000,
        null=False,
        blank=False
    )
    destinations = models.ManyToManyField(
        Destination,
        related_name='cruises'
    )
    def __str__(self):
        return self.name

class InfoRequest(models.Model):
    """
    Modelo para solicitudes de información sobre cruceros.
    Los usuarios completan este formulario para recibir más detalles.
    """
    name = models.CharField(
        max_length=50,
        null=False,
        blank=False,
        verbose_name='Nombre completo',
        help_text='Ingrese su nombre completo (máximo 50 caracteres)',
        error_messages={
            'blank': 'Por favor, ingrese su nombre completo.',
            'null': 'El nombre es obligatorio.',
            'max_length': 'El nombre no puede tener más de 50 caracteres.',
            'required': 'El nombre es un campo obligatorio.',
        }
    )
    email = models.EmailField(
        null=False,
        blank=False,
        verbose_name='Correo electrónico',
        help_text='Ingrese un correo electrónico válido',
        error_messages={
            'blank': 'Por favor, ingrese su correo electrónico.',
            'null': 'El correo electrónico es obligatorio.',
            'invalid': 'Ingrese un correo electrónico válido (ejemplo: usuario@dominio.com).',
            'required': 'El correo electrónico es un campo obligatorio.',
        }
    )
    notes = models.CharField(
        max_length=2000,
        null=False,
        blank=False,
        verbose_name='Mensaje',
        help_text='Déjenos su consulta o comentario (máximo 2000 caracteres)',
        error_messages={
            'blank': 'Por favor, déjenos un mensaje con su consulta.',
            'null': 'El mensaje es obligatorio.',
            'max_length': 'El mensaje no puede tener más de 2000 caracteres.',
            'required': 'El mensaje es un campo obligatorio.',
        }
    )
    cruise = models.ForeignKey(
        Cruise,
        on_delete=models.PROTECT,
        null=False,
        blank=False,
        verbose_name='Crucero de interés',
        help_text='Seleccione el crucero sobre el que desea información',
        error_messages={
            'blank': 'Por favor, seleccione un crucero.',
            'null': 'Debe seleccionar un crucero.',
            'required': 'Debe seleccionar un crucero de la lista.',
        }
    )
    
    class Meta:
        verbose_name = 'Solicitud de información'
        verbose_name_plural = 'Solicitudes de información'
        ordering = ['-id']  # Más recientes primero
    
    def __str__(self):
        return f"{self.name} - {self.cruise.name}"


class Review(models.Model):
    """
    Modelo para las opiniones/reviews de los destinos
    """
    # Constantes
    MIN_RATING = 1
    MAX_RATING = 5
    MAX_COMMENT_LENGTH = 1000
    
    destination = models.ForeignKey(
        Destination,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Destino',
        help_text='Destino al que pertenece la review',
    )
    user = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Usuario',
        help_text='Usuario que escribió la review',
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(MIN_RATING), MaxValueValidator(MAX_RATING)],
        verbose_name='Calificación',
        help_text=f'Calificación del destino (entre {MIN_RATING} y {MAX_RATING})',
    )
    comment = models.TextField(
        max_length=MAX_COMMENT_LENGTH,
        blank=True,
        default='',
        verbose_name='Comentario',
        help_text=f'Comentario sobre el destino (máximo {MAX_COMMENT_LENGTH} caracteres)',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de creación',
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['destination', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.destination.name} ({self.rating}/{self.MAX_RATING})"
    
    def get_rating_display(self):
        """Retorna el rating en formato de estrellas"""
        return '★' * self.rating + '☆' * (self.MAX_RATING - self.rating)
    
    def is_positive(self):
        """Retorna True si la calificación es mayor o igual a 4"""
        return self.rating >= 4
    
    def has_comment(self):
        """Retorna True si la review tiene comentario"""
        return bool(self.comment.strip())
