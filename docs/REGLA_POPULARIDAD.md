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

## Tabla de Validación Completa

A continuación se presenta una tabla con destinos de ejemplo para validar manualmente la regla de popularidad:

| # | Destino | Número de Reviews | Puntuación Media | Posición Esperada | Justificación |
|---|---------|-------------------|------------------|-------------------|---------------|
| 1 | **Marte** | 250 | 4.7 | **1** | Mayor número de reviews del sistema |
| 2 | **Luna Europa** | 200 | 4.9 | **2** | Segundo mayor número de reviews |
| 3 | **Titán** | 200 | 4.6 | **3** | Empate en reviews con Luna Europa, menor puntuación |
| 4 | **Venus** | 150 | 5.0 | **4** | Menos reviews que los anteriores |
| 5 | **Mercurio** | 150 | 4.8 | **5** | Empate con Venus, menor puntuación |
| 6 | **Io** | 150 | 4.5 | **6** | Empate en 150 reviews, menor puntuación |
| 7 | **Ganímedes** | 100 | 5.0 | **7** | Menos reviews que los anteriores |
| 8 | **Calisto** | 100 | 4.9 | **8** | Empate con Ganímedes, menor puntuación |
| 9 | **Encélado** | 100 | 4.3 | **9** | Empate en 100 reviews, menor puntuación |
| 10 | **Plutón** | 75 | 5.0 | **10** | Menos reviews |
| 11 | **Tritón** | 75 | 4.7 | **11** | Empate con Plutón, menor puntuación |
| 12 | **Caronte** | 50 | 4.9 | **12** | Pocos reviews |
| 13 | **Fobos** | 50 | 4.4 | **13** | Empate con Caronte, menor puntuación |
| 14 | **Deimos** | 25 | 5.0 | **14** | Muy pocos reviews |
| 15 | **Ceres** | 25 | 4.2 | **15** | Empate con Deimos, menor puntuación |
| 16 | **Vesta** | 10 | 4.8 | **16** | Apenas reviews |
| 17 | **Pallas** | 5 | 5.0 | **17** | Casi sin reviews |
| 18 | **Sedna** | 0 | 0.0 | **18** | Sin reviews (recién descubierto) |

### Verificación Manual de la Fórmula

**✓ Criterio 1 - Ordenación por número de reviews (descendente):**
- Marte (250) > Luna Europa (200) > Venus (150) > Ganímedes (100) > Plutón (75) > Caronte (50) > Deimos (25) > Vesta (10) > Pallas (5) > Sedna (0)
- **Verificado**: Los destinos están ordenados correctamente por volumen de reviews

**✓ Criterio 2 - Desempate por puntuación media (descendente):**
- Luna Europa (200, 4.9★) > Titán (200, 4.6★) ← Empate en reviews, ordenado por puntuación
- Venus (150, 5.0★) > Mercurio (150, 4.8★) > Io (150, 4.5★) ← Empate triple resuelto por puntuación
- Ganímedes (100, 5.0★) > Calisto (100, 4.9★) > Encélado (100, 4.3★) ← Empate triple resuelto
- **Verificado**: En todos los empates, la mejor puntuación aparece primero

**✓ Combinación de criterios:**
- Ganímedes (100 reviews, 5.0★) > Plutón (75 reviews, 5.0★)
  - A pesar de tener la misma puntuación perfecta, prevalece el que tiene más reviews
- Luna Europa (200, 4.9★) > Venus (150, 5.0★)
  - Aunque Venus tiene puntuación perfecta, Luna Europa tiene más engagement
- **Verificado**: El número de reviews prevalece sobre la puntuación cuando no hay empate

**✓ Casos especiales:**
- Sedna (0 reviews, 0.0★) aparece en última posición
- **Verificado**: Los destinos sin reviews tienen prioridad mínima

### Conclusiones de la Validación

✅ **La regla funciona correctamente** y cumple con las expectativas de producto:

1. **Prioriza el engagement social**: Un destino con más reviews (independientemente de su puntuación) se considera más popular
2. **Calidad como criterio de desempate**: Cuando hay igual número de reviews, gana el de mejor puntuación
3. **Predecible y transparente**: El orden es completamente determinístico y explicable
4. **Incentiva la participación**: Los destinos nuevos necesitan generar reviews para subir en el ranking

### Interpretación de Negocio

- **Marte (250, 4.7★)** es #1 porque tiene el mayor engagement, aunque no tenga puntuación perfecta
- **Venus (150, 5.0★)** es #4 a pesar de su puntuación perfecta, porque tiene menos engagement que los 3 primeros
- **Ganímedes (100, 5.0★)** supera a **Plutón (75, 5.0★)** por tener más tracción social, no por calidad

Esta lógica refleja que **la popularidad real se mide por la cantidad de interacciones**, mientras que la calidad es un refinamiento secundario.

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
- La ordenación se aplica en el queryset antes de enviar los datos a la plantilla
