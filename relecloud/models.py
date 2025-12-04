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
    destination = models.ForeignKey(
        Destination,
        on_delete=models.CASCADE,
        related_name='reviews',
        null=False,
        blank=False,
    )
    user = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='reviews',
        null=False,
        blank=False,
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=False,
        blank=False,
    )
    comment = models.TextField(
        max_length=1000,
        null=False,
        blank=True,
        default='',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
    
    def __str__(self):
        return f"{self.user.username} - {self.destination.name} ({self.rating}/5)"
