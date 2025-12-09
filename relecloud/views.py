from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from . import models
from .forms import RegistroUsuarioForm, ReviewForm
from .services import send_info_request_email
from django.views import generic
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Avg, Count
import logging

# Configurar logger
logger = logging.getLogger(__name__)

# Create your views here.
def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def destinations(request):
    """
    Vista de listado de destinos con calificaciones y conteo de reviews.
    Maneja errores de base de datos para evitar crashes.
    """
    try:
        all_destinations = models.Destination.objects.annotate(
            avg_rating=Avg('reviews__rating'),
            review_count=Count('reviews')
        ).order_by('-review_count', '-avg_rating')
    except Exception as e:
        # Si hay error (ej: tabla no existe), obtener destinos sin anotaciones
        logger.error(f"Error al obtener destinos con anotaciones: {e}")
        all_destinations = models.Destination.objects.all()
    
    return render(request, 'destinations.html', {'destinations': all_destinations})

class DestinationDetailView(generic.DetailView):
    template_name = 'destination_detail.html'
    model = models.Destination
    context_object_name = 'destination'
    
    def get_queryset(self):
        """Optimizar query con prefetch de reviews para evitar N+1"""
        return models.Destination.objects.prefetch_related('reviews__user').annotate(
            avg_rating=Avg('reviews__rating'),
            review_count=Count('reviews')
        )

class CruiseDetailView(generic.DetailView):
    template_name = 'cruise_detail.html'
    model = models.Cruise
    context_object_name = 'cruise'

class InfoRequestCreate(LoginRequiredMixin, SuccessMessageMixin, generic.CreateView):
    """
    Vista para crear solicitudes de información sobre cruceros.
    
    Requiere que el usuario esté autenticado (LoginRequiredMixin).
    Después de guardar la solicitud, envía un correo de notificación
    al administrador con los datos proporcionados por el usuario.
    
    Comportamiento importante:
        - La solicitud SIEMPRE se guarda en la base de datos
        - El envío del correo es independiente del guardado
        - Si el correo falla, se muestra un mensaje de advertencia
          pero la solicitud queda registrada correctamente
        - Los errores de envío se registran en los logs
    
    Attributes:
        template_name: Plantilla HTML para el formulario
        model: Modelo InfoRequest
        fields: Campos del formulario (name, email, cruise, notes)
        success_url: URL de redirección tras éxito (index)
        success_message: Mensaje mostrado al usuario tras guardar
    """
    template_name = 'info_request_create.html'
    model = models.InfoRequest
    fields = ['name', 'email', 'cruise', 'notes']
    success_url = reverse_lazy('index')
    success_message = 'Thank you, %(name)s! We will email you when we have more information about %(cruise)s!'
    
    def form_valid(self, form):
        """
        Procesa el formulario válido: guarda la solicitud y envía correo de notificación.
        
        Flujo de ejecución:
            1. Guardar el formulario en la base de datos (super().form_valid())
            2. Intentar enviar correo de notificación al administrador
            3. Registrar resultado en logs
            4. Mostrar mensaje de advertencia si el envío falla
            5. Retornar respuesta (redirección) independientemente del resultado del correo
        
        Importante: El modelo se guarda SIEMPRE, incluso si el envío del correo falla.
        Esto garantiza que no se pierdan solicitudes de información por problemas
        temporales del servidor de correo.
        
        Args:
            form: Formulario validado con los datos de la solicitud
            
        Returns:
            HttpResponse: Redirección a success_url con mensaje de éxito
        """
        # Guardar el formulario y obtener la instancia creada
        # super().form_valid() ejecuta form.save() y guarda la instancia en self.object
        response = super().form_valid(form)
        
        # Intentar enviar el correo de notificación
        # El envío NO debe afectar el guardado de la solicitud
        try:
            # Llamar al servicio de envío de correo
            # send_info_request_email() retorna True/False sin lanzar excepciones
            email_sent = send_info_request_email(self.object)
            
            if email_sent:
                # Correo enviado exitosamente
                # El log ya fue registrado por la función send_info_request_email()
                logger.info(
                    f"Correo de notificación enviado para solicitud de información. "
                    f"ID: {self.object.id}, Usuario: {self.object.name}"
                )
            else:
                # El envío falló pero ya está registrado en el log por el servicio
                # Mostrar mensaje de advertencia al usuario para que sepa que
                # su solicitud fue guardada pero la notificación falló
                messages.warning(
                    self.request,
                    'Tu solicitud ha sido guardada, pero hubo un problema al enviar la notificación por correo.'
                )
                
        except Exception as e:
            # Error inesperado al intentar enviar el correo
            # Este bloque solo se ejecuta si send_info_request_email() lanza una excepción
            # (aunque está diseñado para NO lanzarlas, este es un safety net)
            # La solicitud ya está guardada en la BD, solo notificamos el problema
            logger.error(
                f"Error inesperado al intentar enviar correo de notificación. "
                f"InfoRequest ID: {self.object.id}. Error: {str(e)}"
            )
            messages.warning(
                self.request,
                'Tu solicitud ha sido guardada, pero hubo un problema al enviar la notificación por correo.'
            )
        
        # Retornar la respuesta original (redirección a success_url)
        # El modelo ya está guardado independientemente del resultado del envío de correo
        # El usuario verá el success_message en la página de destino
        return response


class RegistroUsuarioCreate(SuccessMessageMixin, generic.CreateView):
    template_name = 'registro.html'
    form_class = RegistroUsuarioForm
    success_url = reverse_lazy('index')
    success_message = '¡Registro exitoso! Bienvenido %(username)s.'


class ReviewCreateView(LoginRequiredMixin, generic.CreateView):
    """
    Vista para crear reviews de destinos
    Requiere que el usuario esté autenticado y tenga una compra (InfoRequest)
    """
    model = models.Review
    form_class = ReviewForm
    template_name = 'review_create.html'
    
    def dispatch(self, request, *args, **kwargs):
        """Obtener el destino antes de procesar la petición"""
        self.destination = get_object_or_404(models.Destination, pk=self.kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        """Agregar el destino al contexto"""
        context = super().get_context_data(**kwargs)
        context['destination'] = self.destination
        return context
    
    def form_valid(self, form):
        """Validar que el usuario tenga compra y no tenga review duplicada"""
        # Verificar si el usuario ya tiene una review para este destino
        existing_review = models.Review.objects.filter(
            user=self.request.user,
            destination=self.destination
        ).first()
        
        if existing_review:
            messages.error(self.request, 'Ya has enviado una review para este destino.')
            return redirect('destination_detail', pk=self.destination.pk)
        
        # Verificar si el usuario tiene una compra (InfoRequest) para un crucero que incluya este destino
        has_purchase = models.InfoRequest.objects.filter(
            email=self.request.user.email,
            cruise__destinations=self.destination
        ).exists()
        
        if not has_purchase:
            messages.error(
                self.request,
                'No estás autorizado para dejar una review. Debes tener una compra para este destino.'
            )
            return redirect('destination_detail', pk=self.destination.pk)
        
        # Asignar usuario y destino
        form.instance.user = self.request.user
        form.instance.destination = self.destination
        
        # Llamar a full_clean() para validar el modelo
        try:
            form.instance.full_clean()
        except Exception as e:
            messages.error(self.request, f'Error de validación: {str(e)}')
            return self.form_invalid(form)
        
        messages.success(self.request, 'Tu review ha sido publicada exitosamente.')
        return super().form_valid(form)
    
    def get_success_url(self):
        """Redirigir al detalle del destino"""
        return reverse('destination_detail', kwargs={'pk': self.destination.pk})
