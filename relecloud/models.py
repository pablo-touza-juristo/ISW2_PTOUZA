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
    name = models.CharField(
        max_length=50,
        null=False,
        blank=False,
    )
    email = models.EmailField()
    notes = models.TextField(
        max_length=2000,
        null=False,
        blank=False
    )
    cruise = models.ForeignKey(
        Cruise,
        on_delete=models.PROTECT
    )


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
        blank=True
    )
    
    def __str__(self):
        return self.name
    
    @property
    def image_url(self):
        if self.image:
            return self.image.url
        return '/static/res/img/placeholder.png'  # Ruta al placeholder
