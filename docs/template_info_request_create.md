# Documentación del Template: info_request_create.html

## 1. Renderizado de errores

### Errores generales del formulario
- **`form.non_field_errors`**: Errores no asociados a campos específicos
- Se muestran en un alert rojo (`alert-danger`) con icono de advertencia
- Dismissible (se pueden cerrar)

### Errores en campos específicos
- **`form.errors`**: Comprueba si hay errores en cualquier campo
- Se muestra un alert amarillo (`alert-warning`) informativo
- `crispy_forms` renderiza automáticamente los errores de cada campo debajo del mismo

## 2. Estilos de errores (Bootstrap 5)

- **`alert-danger`**: Para errores generales del formulario (rojo)
- **`alert-warning`**: Para avisos cuando hay errores en campos (amarillo)
- **`is-invalid`**: Clase aplicada automáticamente por crispy_forms a campos con errores
- **`invalid-feedback`**: Clase de Bootstrap para mostrar mensajes de error debajo de cada campo

## 3. Validación del formulario

- **`novalidate`**: Desactiva la validación HTML5 del navegador
- Django/crispy_forms manejan toda la validación en el servidor
- Los errores se muestran después del POST si la validación falla
- Los valores válidos ingresados se mantienen en los campos

## 4. Accesibilidad

- **`role="alert"`**: Para lectores de pantalla
- **`aria-label`**: En botones de cierre
- Iconos de Bootstrap Icons para mejor UX visual
- Estructura semántica correcta (headings, labels, etc.)

## 5. Comportamiento del formulario

### Flujo normal (sin errores):
1. Usuario completa el formulario
2. Hace clic en "Enviar solicitud"
3. Formulario se valida en el servidor
4. Si es válido → Se guarda y redirige con mensaje de éxito
5. Se envía email de notificación al administrador

### Flujo con errores:
1. Usuario envía el formulario con datos inválidos
2. Formulario se valida en el servidor
3. Django detecta errores de validación
4. El formulario se vuelve a renderizar mostrando:
   - Alert amarillo general arriba
   - Mensajes de error específicos debajo de cada campo inválido
   - Los valores válidos se mantienen en los campos
   - Los campos inválidos tienen borde rojo

## 6. Renderizado con crispy_forms

```django
{{ form|crispy }}
```

Este filtro hace que crispy_forms:
- Renderice automáticamente todos los campos del formulario
- Aplique estilos de Bootstrap 5
- Muestre los `help_text` definidos en el modelo
- Muestre errores de validación debajo de cada campo
- Marque campos inválidos con la clase `is-invalid`
- Aplique la clase `form-control` a inputs
- Maneje correctamente diferentes tipos de campos (text, email, select, textarea)

## 7. Estructura del formulario

### Campos renderizados (orden):
1. **Nombre completo** (`name`)
   - CharField, máximo 50 caracteres
   - Obligatorio
   - Help text: "Ingrese su nombre completo (máximo 50 caracteres)"

2. **Correo electrónico** (`email`)
   - EmailField, valida formato
   - Obligatorio
   - Help text: "Ingrese un correo electrónico válido"

3. **Crucero de interés** (`cruise`)
   - ForeignKey, dropdown con cruceros disponibles
   - Obligatorio
   - Help text: "Seleccione el crucero sobre el que desea información"

4. **Mensaje** (`notes`)
   - CharField, máximo 2000 caracteres
   - Obligatorio
   - Help text: "Déjenos su consulta o comentario (máximo 2000 caracteres)"

## 8. Botones

- **Cancelar**: Vuelve a la página de inicio (`{% url 'index' %}`)
- **Enviar solicitud**: Envía el formulario (POST)

## 9. Mensajes de validación

Los mensajes de error se generan automáticamente por Django basándose en:
- Validaciones del modelo (blank=False, max_length, etc.)
- Validadores de campo (EmailValidator para EmailField)
- Mensajes por defecto de Django (en español si `LANGUAGE_CODE='es'`)

## 10. Dependencias

- **crispy_forms**: Para renderizado de formularios
- **crispy_bootstrap5**: Para estilos Bootstrap 5
- **Bootstrap 5**: CSS framework
- **Bootstrap Icons**: Para iconos en alertas y botones
