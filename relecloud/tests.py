from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from .models import Destination, Review, Usuario, Cruise, InfoRequest
from datetime import datetime

# Create your tests here.

class ReviewModelTest(TestCase):
    """Tests para el modelo Review"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        # Crear un usuario de prueba
        self.user = Usuario.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        # Crear un destino de prueba
        self.destination = Destination.objects.create(
            name='Luna',
            description='Nuestro satélite natural'
        )
    
    def test_create_review_with_valid_data(self):
        """Test: Crear una review con datos válidos"""
        review = Review.objects.create(
            destination=self.destination,
            user=self.user,
            rating=5,
            comment='Excelente destino, muy recomendado!'
        )
        
        self.assertEqual(review.destination, self.destination)
        self.assertEqual(review.user, self.user)
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.comment, 'Excelente destino, muy recomendado!')
        self.assertIsNotNone(review.created_at)
    
    def test_review_str_method(self):
        """Test: Método __str__ de Review"""
        review = Review.objects.create(
            destination=self.destination,
            user=self.user,
            rating=4,
            comment='Muy bueno'
        )
        
        expected_str = f"{self.user.username} - {self.destination.name} (4/5)"
        self.assertEqual(str(review), expected_str)
    
    def test_review_rating_must_be_between_1_and_5(self):
        """Test: El rating debe estar entre 1 y 5"""
        # Rating menor a 1 debe fallar
        with self.assertRaises(ValidationError):
            review = Review(
                destination=self.destination,
                user=self.user,
                rating=0,
                comment='Rating inválido'
            )
            review.full_clean()
        
        # Rating mayor a 5 debe fallar
        with self.assertRaises(ValidationError):
            review = Review(
                destination=self.destination,
                user=self.user,
                rating=6,
                comment='Rating inválido'
            )
            review.full_clean()
    
    def test_review_requires_destination(self):
        """Test: Una review requiere un destino"""
        with self.assertRaises(IntegrityError):
            Review.objects.create(
                user=self.user,
                rating=5,
                comment='Sin destino'
            )
    
    def test_review_requires_user(self):
        """Test: Una review requiere un usuario"""
        with self.assertRaises(IntegrityError):
            Review.objects.create(
                destination=self.destination,
                rating=5,
                comment='Sin usuario'
            )
    
    def test_review_requires_rating(self):
        """Test: Una review requiere un rating"""
        with self.assertRaises(IntegrityError):
            Review.objects.create(
                destination=self.destination,
                user=self.user,
                comment='Sin rating'
            )
    
    def test_comment_is_optional(self):
        """Test: El comentario es opcional"""
        review = Review.objects.create(
            destination=self.destination,
            user=self.user,
            rating=5,
            comment=''
        )
        
        self.assertEqual(review.comment, '')
    
    def test_user_can_review_same_destination_multiple_times(self):
        """Test: Un usuario puede hacer múltiples reviews del mismo destino"""
        review1 = Review.objects.create(
            destination=self.destination,
            user=self.user,
            rating=4,
            comment='Primera visita'
        )
        
        review2 = Review.objects.create(
            destination=self.destination,
            user=self.user,
            rating=5,
            comment='Segunda visita, mucho mejor'
        )
        
        self.assertEqual(Review.objects.filter(
            destination=self.destination,
            user=self.user
        ).count(), 2)
    
    def test_destination_reviews_relationship(self):
        """Test: Relación entre destino y reviews"""
        Review.objects.create(
            destination=self.destination,
            user=self.user,
            rating=5,
            comment='Review 1'
        )
        
        user2 = Usuario.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123',
            first_name='Test2',
            last_name='User2'
        )
        
        Review.objects.create(
            destination=self.destination,
            user=user2,
            rating=4,
            comment='Review 2'
        )
        
        self.assertEqual(self.destination.reviews.count(), 2)
    
    def test_review_ordering_by_created_at_desc(self):
        """Test: Las reviews se ordenan por fecha de creación descendente"""
        review1 = Review.objects.create(
            destination=self.destination,
            user=self.user,
            rating=5,
            comment='Primera review'
        )
        
        user2 = Usuario.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123',
            first_name='Test2',
            last_name='User2'
        )
        
        review2 = Review.objects.create(
            destination=self.destination,
            user=user2,
            rating=4,
            comment='Segunda review'
        )
        
        reviews = Review.objects.all()
        self.assertEqual(reviews[0], review2)  # La más reciente primero
        self.assertEqual(reviews[1], review1)


class ReviewViewTest(TestCase):
    """Tests para las vistas de Review"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        # Crear usuarios
        self.user_without_purchase = Usuario.objects.create_user(
            username='user_no_compra',
            email='nocompra@example.com',
            password='testpass123',
            first_name='Usuario',
            last_name='Sin Compra'
        )
        
        self.user_with_purchase = Usuario.objects.create_user(
            username='user_con_compra',
            email='concompra@example.com',
            password='testpass123',
            first_name='Usuario',
            last_name='Con Compra'
        )
        
        # Crear destino
        self.destination = Destination.objects.create(
            name='Marte',
            description='El planeta rojo'
        )
        
        # Crear crucero
        self.cruise = Cruise.objects.create(
            name='Expedición a Marte',
            description='Viaje de 2 semanas al planeta rojo'
        )
        self.cruise.destinations.add(self.destination)
        
        # Crear InfoRequest (simulando compra) para user_with_purchase
        self.info_request = InfoRequest.objects.create(
            name=self.user_with_purchase.get_full_name(),
            email=self.user_with_purchase.email,
            cruise=self.cruise,
            notes='Quiero información'
        )
        
        # URL para crear review
        self.create_review_url = f'/destination/{self.destination.id}/review/create/'
    
    def test_unauthenticated_user_redirected_to_login(self):
        """Test: Usuario no autenticado es redirigido al login"""
        response = self.client.get(self.create_review_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)
    
    def test_unauthenticated_user_post_redirected_to_login(self):
        """Test: POST de usuario no autenticado redirige al login"""
        response = self.client.post(self.create_review_url, {
            'rating': 5,
            'comment': 'Excelente destino'
        })
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)
        self.assertEqual(Review.objects.count(), 0)
    
    def test_authenticated_user_without_purchase_cannot_create_review(self):
        """Test: Usuario autenticado sin compra no puede crear review"""
        self.client.login(username='user_no_compra', password='testpass123')
        
        response = self.client.post(self.create_review_url, {
            'rating': 5,
            'comment': 'Intento de review sin compra'
        })
        
        # No debería crear la review
        self.assertEqual(Review.objects.count(), 0)
        
        # Debería mostrar mensaje de error
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any('compra' in str(m).lower() or 'autorizado' in str(m).lower() for m in messages))
    
    def test_authenticated_user_with_purchase_can_create_review(self):
        """Test: Usuario autenticado con compra puede crear review"""
        self.client.login(username='user_con_compra', password='testpass123')
        
        response = self.client.post(self.create_review_url, {
            'rating': 5,
            'comment': 'Excelente experiencia en Marte'
        }, follow=True)
        
        # Debería crear la review
        self.assertEqual(Review.objects.count(), 1)
        
        review = Review.objects.first()
        self.assertEqual(review.user, self.user_with_purchase)
        self.assertEqual(review.destination, self.destination)
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.comment, 'Excelente experiencia en Marte')
        
        # Debería redirigir al detalle del destino
        self.assertRedirects(response, f'/destination/{self.destination.id}')
    
    def test_user_cannot_create_duplicate_review(self):
        """Test: Usuario no puede crear segunda review del mismo destino"""
        self.client.login(username='user_con_compra', password='testpass123')
        
        # Crear primera review
        Review.objects.create(
            destination=self.destination,
            user=self.user_with_purchase,
            rating=4,
            comment='Primera review'
        )
        
        # Intentar crear segunda review
        response = self.client.post(self.create_review_url, {
            'rating': 5,
            'comment': 'Intento de segunda review'
        })
        
        # Solo debería existir una review
        self.assertEqual(Review.objects.filter(
            user=self.user_with_purchase,
            destination=self.destination
        ).count(), 1)
        
        # Debería mostrar mensaje de error
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any('ya has enviado' in str(m).lower() or 'ya existe' in str(m).lower() for m in messages))
    
    def test_create_review_form_displays_correctly(self):
        """Test: Formulario de creación de review se muestra correctamente"""
        self.client.login(username='user_con_compra', password='testpass123')
        
        response = self.client.get(self.create_review_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'rating')
        self.assertContains(response, 'comment')
    
    def test_invalid_rating_rejected(self):
        """Test: Rating inválido es rechazado"""
        self.client.login(username='user_con_compra', password='testpass123')
        
        # Rating fuera de rango
        response = self.client.post(self.create_review_url, {
            'rating': 6,
            'comment': 'Rating inválido'
        })
        
        self.assertEqual(Review.objects.count(), 0)
        self.assertEqual(response.status_code, 200)  # Vuelve a mostrar el formulario
    
    def test_review_without_comment_is_valid(self):
        """Test: Review sin comentario es válida"""
        self.client.login(username='user_con_compra', password='testpass123')
        
        response = self.client.post(self.create_review_url, {
            'rating': 4,
            'comment': ''
        }, follow=True)
        
        self.assertEqual(Review.objects.count(), 1)
        review = Review.objects.first()
        self.assertEqual(review.comment, '')
