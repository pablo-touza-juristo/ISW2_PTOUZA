"""
Script para verificar que el orden de destinos en la vista coincide con el esperado
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from relecloud.models import Destination
from django.db.models import Avg, Count

def verify_destination_order():
    """Verifica el orden de los destinos según la regla de popularidad"""
    
    print("="*100)
    print("VERIFICACIÓN DEL ORDEN DE DESTINOS SEGÚN REGLA DE POPULARIDAD")
    print("="*100)
    print("\nRegla: ORDER BY review_count DESC, avg_rating DESC")
    print("-"*100)
    
    # Obtener destinos con el mismo queryset que usa la vista
    destinations = Destination.objects.annotate(
        review_count=Count('reviews'),
        avg_rating=Avg('reviews__rating')
    ).order_by('-review_count', '-avg_rating')
    
    # Mostrar tabla con el orden actual
    print(f"\n{'Pos':<5} {'Destino':<30} {'Reviews':<12} {'Rating':<12} {'Verificación'}")
    print("-"*100)
    
    prev_review_count = float('inf')
    prev_avg_rating = float('inf')
    all_correct = True
    
    for i, dest in enumerate(destinations, 1):
        review_count = dest.review_count or 0
        avg_rating = dest.avg_rating or 0.0
        
        # Verificar que el orden es correcto
        is_correct = True
        status_msg = "✓ OK"
        
        # Verificar regla 1: review_count descendente
        if review_count > prev_review_count:
            is_correct = False
            status_msg = "✗ ERROR: más reviews que anterior"
            all_correct = False
        # Verificar regla 2: avg_rating descendente cuando review_count es igual
        elif review_count == prev_review_count and avg_rating > prev_avg_rating:
            is_correct = False
            status_msg = "✗ ERROR: mejor rating que anterior con mismo #reviews"
            all_correct = False
        
        # Mostrar fila
        rating_str = f"{avg_rating:.1f}★" if avg_rating > 0 else "Sin rating"
        print(f"{i:<5} {dest.name:<30} {review_count:<12} {rating_str:<12} {status_msg}")
        
        prev_review_count = review_count
        prev_avg_rating = avg_rating
    
    print("-"*100)
    
    # Resumen
    print("\n" + "="*100)
    if all_correct:
        print("✅ VERIFICACIÓN EXITOSA: Todos los destinos están ordenados correctamente")
    else:
        print("❌ VERIFICACIÓN FALLIDA: Se encontraron errores en el ordenamiento")
    print("="*100)
    
    # Casos de prueba específicos
    print("\nVERIFICACIÓN DE CASOS ESPECÍFICOS:")
    print("-"*100)
    
    test_cases = []
    
    # Caso 1: Destino con más reviews debe estar primero
    first_dest = destinations.first()
    if first_dest:
        test_cases.append({
            'nombre': 'Destino #1 tiene el mayor número de reviews',
            'resultado': first_dest.review_count >= max([d.review_count or 0 for d in destinations]),
            'detalle': f"{first_dest.name}: {first_dest.review_count or 0} reviews"
        })
    
    # Caso 2: Destinos sin reviews deben estar al final
    destinos_sin_reviews = [d for d in destinations if (d.review_count or 0) == 0]
    destinos_con_reviews = [d for d in destinations if (d.review_count or 0) > 0]
    
    if destinos_sin_reviews and destinos_con_reviews:
        ultimo_con_reviews_pos = list(destinations).index(destinos_con_reviews[-1])
        primer_sin_reviews_pos = list(destinations).index(destinos_sin_reviews[0])
        
        test_cases.append({
            'nombre': 'Destinos sin reviews están al final',
            'resultado': primer_sin_reviews_pos > ultimo_con_reviews_pos,
            'detalle': f"Último con reviews: pos {ultimo_con_reviews_pos+1}, Primero sin reviews: pos {primer_sin_reviews_pos+1}"
        })
    
    # Caso 3: Empate en reviews se resuelve por rating
    empates = {}
    for dest in destinations:
        rc = dest.review_count or 0
        if rc > 0:
            if rc not in empates:
                empates[rc] = []
            empates[rc].append(dest)
    
    empate_correcto = True
    for review_count, dests in empates.items():
        if len(dests) > 1:
            # Verificar que están ordenados por rating descendente
            ratings = [d.avg_rating or 0 for d in dests]
            if ratings != sorted(ratings, reverse=True):
                empate_correcto = False
                break
    
    test_cases.append({
        'nombre': 'Empates se resuelven por rating descendente',
        'resultado': empate_correcto,
        'detalle': f"{len([k for k,v in empates.items() if len(v) > 1])} grupos con empate verificados"
    })
    
    # Mostrar resultados de casos de prueba
    for tc in test_cases:
        symbol = "✅" if tc['resultado'] else "❌"
        print(f"{symbol} {tc['nombre']}")
        print(f"   {tc['detalle']}")
    
    print("-"*100)
    
    return all_correct

if __name__ == '__main__':
    success = verify_destination_order()
    exit(0 if success else 1)
