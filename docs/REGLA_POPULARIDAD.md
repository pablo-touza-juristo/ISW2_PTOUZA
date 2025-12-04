# Regla de Popularidad de Destinos

## Definición

La popularidad de un destino en el sistema ReleCloud se determina mediante la siguiente regla de ordenación.

## Criterios de Ordenación

Los destinos se ordenarán según los siguientes criterios, aplicados en orden de prioridad:

1. **Número de reviews (descendente)**: El destino con mayor cantidad de reviews se considera más popular.

2. **Puntuación media (descendente)**: En caso de empate en el número de reviews, se ordenará por la puntuación media más alta.

## Fórmula de Ordenación

```sql
ORDER BY:
  1. review_count DESC
  2. avg_rating DESC (en caso de empate)
```

## Implementación en Django ORM

```python
Destination.objects.annotate(
    review_count=Count('reviews'),
    avg_rating=Avg('reviews__rating')
).order_by('-review_count', '-avg_rating')
```

## Justificación

Esta regla prioriza:
- **Engagement**: Un mayor número de reviews indica que el destino ha generado más interés y participación de los usuarios.
- **Calidad**: En caso de empate, se favorece el destino con mejor puntuación media.
- **Transparencia**: La regla es clara, predecible y fácil de entender para los usuarios.

## Ejemplos Prácticos

### Ejemplo 1: Sin empate en reviews
- **Destino A**: 100 reviews, 4.5★ → **Posición 1** (más reviews)
- **Destino B**: 50 reviews, 5.0★ → **Posición 2** (menos reviews, aunque tenga mejor puntuación)

### Ejemplo 2: Empate en número de reviews
- **Destino A**: 50 reviews, 4.8★ → **Posición 1** (mayor puntuación)
- **Destino B**: 50 reviews, 4.5★ → **Posición 2** (menor puntuación)
- **Destino C**: 50 reviews, 4.2★ → **Posición 3** (menor puntuación)

### Ejemplo 3: Ordenación mixta
- **Destino A**: 100 reviews, 4.0★ → **Posición 1** (más reviews)
- **Destino B**: 80 reviews, 5.0★ → **Posición 2** (segundo en reviews)
- **Destino C**: 80 reviews, 4.8★ → **Posición 3** (empate en reviews, menor puntuación que B)
- **Destino D**: 50 reviews, 5.0★ → **Posición 4** (menos reviews)

## Casos Especiales

### Destinos sin reviews
Los destinos sin reviews tendrán:
- `review_count = 0`
- `avg_rating = NULL` (o 0.0 según implementación)
- Aparecerán al final del listado ordenado

### Destinos nuevos
Un destino recién añadido sin reviews aparecerá al final hasta que reciba su primera valoración.

## Notas Técnicas

- Las reviews deben estar asociadas al destino mediante la relación `reviews` (ForeignKey).
- La puntuación media se calcula como el promedio aritmético de todas las puntuaciones.
- Los valores NULL en `avg_rating` se tratarán como menores que cualquier valor numérico.
- La ordenación se aplica en el queryset antes de enviar los datos a la plantilla.
