"""
Script para cargar datos de prueba que validen la regla de popularidad.
Crea destinos con diferentes números de reviews y puntuaciones medias.
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from relecloud.models import Destination, Usuario, Review
from django.db import transaction

def clear_test_data():
    """Elimina datos de prueba existentes"""
    print("Eliminando datos de prueba previos...")
    Review.objects.all().delete()
    Destination.objects.filter(name__in=[
        'Marte', 'Luna Europa', 'Titán', 'Venus', 'Mercurio', 'Io',
        'Ganímedes', 'Calisto', 'Encélado', 'Plutón', 'Tritón',
        'Caronte', 'Fobos', 'Deimos', 'Ceres', 'Vesta', 'Pallas', 'Sedna'
    ]).delete()
    print("✓ Datos previos eliminados")

def create_test_user():
    """Crea o obtiene un usuario de prueba"""
    user, created = Usuario.objects.get_or_create(
        username='testuser',
        defaults={
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User'
        }
    )
    if created:
        user.set_password('testpass123')
        user.save()
        print(f"✓ Usuario de prueba creado: {user.username}")
    else:
        print(f"✓ Usando usuario existente: {user.username}")
    return user

def create_destinations_and_reviews():
    """Crea destinos con diferentes números de reviews según la tabla de validación"""
    
    # Datos según la tabla de validación del documento REGLA_POPULARIDAD.md
    test_data = [
        # (nombre, descripción, num_reviews, avg_rating, posición_esperada)
        ('Marte', 'El planeta rojo, famoso por sus tormentas de polvo', 250, 4.7, 1),
        ('Luna Europa', 'Luna de Júpiter con océanos bajo su superficie helada', 200, 4.9, 2),
        ('Titán', 'La luna más grande de Saturno con atmósfera densa', 200, 4.6, 3),
        ('Venus', 'El planeta más caliente del sistema solar', 150, 5.0, 4),
        ('Mercurio', 'El planeta más cercano al Sol', 150, 4.8, 5),
        ('Io', 'Luna volcánica de Júpiter', 150, 4.5, 6),
        ('Ganímedes', 'La luna más grande del sistema solar', 100, 5.0, 7),
        ('Calisto', 'Luna helada con numerosos cráteres', 100, 4.9, 8),
        ('Encélado', 'Luna de Saturno con géiseres de agua', 100, 4.3, 9),
        ('Plutón', 'Planeta enano en el cinturón de Kuiper', 75, 5.0, 10),
        ('Tritón', 'Luna retrógrada de Neptuno', 75, 4.7, 11),
        ('Caronte', 'La luna más grande de Plutón', 50, 4.9, 12),
        ('Fobos', 'Luna irregular de Marte', 50, 4.4, 13),
        ('Deimos', 'La luna más pequeña de Marte', 25, 5.0, 14),
        ('Ceres', 'Planeta enano en el cinturón de asteroides', 25, 4.2, 15),
        ('Vesta', 'Uno de los asteroides más grandes', 10, 4.8, 16),
        ('Pallas', 'Asteroide del cinturón principal', 5, 5.0, 17),
        ('Sedna', 'Objeto transneptuniano recientemente descubierto', 0, 0.0, 18),
    ]
    
    user = create_test_user()
    
    print("\nCreando destinos y reviews...")
    with transaction.atomic():
        for name, description, num_reviews, avg_rating, expected_pos in test_data:
            # Crear destino
            destination, created = Destination.objects.get_or_create(
                name=name,
                defaults={'description': description}
            )
            
            if created:
                print(f"\n✓ Destino creado: {name}")
            else:
                print(f"\n✓ Destino existente: {name}")
            
            # Crear reviews para alcanzar el promedio deseado
            if num_reviews > 0:
                # Distribuir las calificaciones para obtener el promedio deseado
                ratings = distribute_ratings(num_reviews, avg_rating)
                
                # Crear múltiples usuarios si es necesario para las reviews
                for i, rating in enumerate(ratings):
                    review_user, _ = Usuario.objects.get_or_create(
                        username=f'user_{name.lower().replace(" ", "_")}_{i}',
                        defaults={
                            'email': f'user_{name.lower().replace(" ", "_")}_{i}@example.com',
                            'first_name': f'User{i}',
                            'last_name': name
                        }
                    )
                    
                    Review.objects.create(
                        destination=destination,
                        user=review_user,
                        rating=rating,
                        comment=f'Review de prueba #{i+1} para {name}'
                    )
                
                print(f"  → {num_reviews} reviews creadas (promedio: {avg_rating}★)")
                print(f"  → Posición esperada: #{expected_pos}")
            else:
                print(f"  → Sin reviews (debe aparecer último)")

def distribute_ratings(count, target_avg):
    """
    Distribuye calificaciones para alcanzar un promedio objetivo.
    """
    ratings = []
    total_needed = int(count * target_avg)
    
    # Llenar con calificaciones de 5 y ajustar con calificaciones menores
    fives = total_needed // 5
    remainder = total_needed % 5
    
    # Agregar tantos 5 como sea posible
    ratings.extend([5] * min(fives, count))
    
    # Completar el resto
    remaining_count = count - len(ratings)
    if remaining_count > 0:
        if remainder > 0:
            ratings.append(remainder)
            remaining_count -= 1
        
        # Llenar con valores promedio
        avg_value = int(target_avg)
        ratings.extend([avg_value] * remaining_count)
    
    # Ajustar para que el promedio sea exacto
    while len(ratings) < count:
        ratings.append(int(target_avg))
    
    return ratings[:count]

def verify_ordering():
    """Verifica que el ordenamiento sea correcto"""
    print("\n" + "="*80)
    print("VERIFICACIÓN DEL ORDENAMIENTO")
    print("="*80)
    
    from django.db.models import Avg, Count
    
    destinations = Destination.objects.annotate(
        review_count=Count('reviews'),
        avg_rating=Avg('reviews__rating')
    ).order_by('-review_count', '-avg_rating')
    
    print(f"\n{'#':<4} {'Destino':<20} {'Reviews':<10} {'Rating':<10} {'Estado'}")
    print("-" * 80)
    
    for i, dest in enumerate(destinations, 1):
        review_count = dest.review_count or 0
        avg_rating = dest.avg_rating or 0.0
        status = "✓" if review_count > 0 or i == destinations.count() else "✗"
        
        print(f"{i:<4} {dest.name:<20} {review_count:<10} {avg_rating:<10.1f} {status}")
    
    print("\n" + "="*80)
    print("Verificación completada")
    print("="*80)

def main():
    """Función principal"""
    print("="*80)
    print("CARGA DE DATOS DE PRUEBA - REGLA DE POPULARIDAD")
    print("="*80)
    
    clear_test_data()
    create_destinations_and_reviews()
    verify_ordering()
    
    print("\n✅ Datos de prueba cargados exitosamente")
    print("\n👉 Ahora puedes abrir http://127.0.0.1:8000/destinations/ en el navegador")
    print("   para verificar el ordenamiento visual")

if __name__ == '__main__':
    main()
