from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from .models import Destination, Review, Usuario
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
