from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from . import models
from .forms import RegistroUsuarioForm, ReviewForm
from django.views import generic
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Avg, Count

# Create your views here.
def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def destinations(request):
    all_destinations = models.Destination.objects.annotate(
        avg_rating=Avg('reviews__rating'),
        review_count=Count('reviews')
    ).all()
    return render(request, 'destinations.html', { 'destinations': all_destinations})

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
    template_name = 'info_request_create.html'
    model = models.InfoRequest
    fields = ['name', 'email', 'cruise', 'notes']
    success_url = reverse_lazy('index')
    success_message = 'Thank you, %(name)s! We will email you when we have more information about %(cruise)s!'


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
