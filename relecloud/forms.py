from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import Usuario


class RegistroUsuarioForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ('username', 'first_name', 'last_name', 'email', 'telefono', 'password1', 'password2')
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Usuario.objects.filter(email=email).exists():
            raise ValidationError('Este correo electrónico ya está registrado.')
        return email
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if Usuario.objects.filter(username=username).exists():
            raise ValidationError('Este nombre de usuario ya está en uso.')
        return username
    
    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if not first_name:
            raise ValidationError('El nombre es obligatorio.')
        return first_name
    
    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if not last_name:
            raise ValidationError('Los apellidos son obligatorios.')
        return last_name
