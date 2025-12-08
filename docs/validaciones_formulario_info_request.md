# Validaciones del Formulario InfoRequest

## Descripción General

El formulario de **Solicitud de Información** (`InfoRequest`) implementa validaciones exhaustivas para garantizar la calidad de los datos ingresados por los usuarios y proporcionar mensajes de error claros y útiles.

---

## Campos del Formulario

### 1. Nombre completo (`name`)

**Tipo:** CharField  
**Obligatorio:** Sí  
**Longitud máxima:** 50 caracteres

#### Validaciones:
- ✅ No puede estar vacío
- ✅ Máximo 50 caracteres
- ✅ Debe contener texto válido

#### Mensajes de error:
- **Campo vacío:** "Por favor, ingrese su nombre completo."
- **Demasiado largo:** "El nombre no puede tener más de 50 caracteres."
- **Campo requerido:** "El nombre es un campo obligatorio."

#### Ayuda mostrada al usuario:
*"Ingrese su nombre completo (máximo 50 caracteres)"*

---

### 2. Correo electrónico (`email`)

**Tipo:** EmailField  
**Obligatorio:** Sí  
**Validador:** EmailValidator (formato estándar de email)

#### Validaciones:
- ✅ No puede estar vacío
- ✅ Debe tener formato válido (usuario@dominio.extensión)
- ✅ Valida que contenga @ y dominio válido

#### Mensajes de error:
- **Campo vacío:** "Por favor, ingrese su correo electrónico."
- **Formato inválido:** "Ingrese un correo electrónico válido (ejemplo: usuario@dominio.com)."
- **Campo requerido:** "El correo electrónico es un campo obligatorio."

#### Ejemplos de emails válidos:
- usuario@ejemplo.com
- nombre.apellido@empresa.es
- contacto+tag@dominio.co.uk

#### Ejemplos de emails inválidos:
- email-sin-arroba
- email@
- @dominio.com
- email@dominio (sin extensión)
- email con espacios@dominio.com

#### Ayuda mostrada al usuario:
*"Ingrese un correo electrónico válido"*

---

### 3. Crucero de interés (`cruise`)

**Tipo:** ForeignKey (Relación con modelo Cruise)  
**Obligatorio:** Sí  
**Widget:** Dropdown/Select

#### Validaciones:
- ✅ Debe seleccionar un crucero de la lista
- ✅ El crucero debe existir en la base de datos
- ✅ No puede estar vacío

#### Mensajes de error:
- **Sin selección:** "Por favor, seleccione un crucero."
- **Valor nulo:** "Debe seleccionar un crucero."
- **Campo requerido:** "Debe seleccionar un crucero de la lista."

#### Ayuda mostrada al usuario:
*"Seleccione el crucero sobre el que desea información"*

---

### 4. Mensaje (`notes`)

**Tipo:** CharField (cambiado de TextField para validar max_length)  
**Obligatorio:** Sí  
**Longitud máxima:** 2000 caracteres

#### Validaciones:
- ✅ No puede estar vacío
- ✅ Máximo 2000 caracteres
- ✅ Debe contener texto válido

#### Mensajes de error:
- **Campo vacío:** "Por favor, déjenos un mensaje con su consulta."
- **Demasiado largo:** "El mensaje no puede tener más de 2000 caracteres."
- **Campo requerido:** "El mensaje es un campo obligatorio."

#### Ayuda mostrada al usuario:
*"Déjenos su consulta o comentario (máximo 2000 caracteres)"*

---

## Implementación Técnica

### Validación en el Modelo

```python
class InfoRequest(models.Model):
    name = models.CharField(
        max_length=50,
        null=False,
        blank=False,
        verbose_name='Nombre completo',
        help_text='Ingrese su nombre completo (máximo 50 caracteres)',
        error_messages={
            'blank': 'Por favor, ingrese su nombre completo.',
            'max_length': 'El nombre no puede tener más de 50 caracteres.',
            'required': 'El nombre es un campo obligatorio.',
        }
    )
    # ... otros campos
```

### Renderizado en el Template

El formulario se renderiza usando **crispy_forms** con Bootstrap 5:

```django
{{ form|crispy }}
```

Esto proporciona automáticamente:
- Etiquetas de campos con `verbose_name`
- Textos de ayuda con `help_text`
- Mensajes de error personalizados
- Estilos Bootstrap (campos inválidos con borde rojo)
- Iconos y alertas de error

---

## Proceso de Validación

### 1. Validación del Cliente (Desactivada)

El template usa `novalidate` para desactivar la validación HTML5 del navegador:

```html
<form method="post" novalidate>
```

**Razón:** Permitir que Django maneje toda la validación en el servidor con mensajes personalizados.

### 2. Validación del Servidor

Cuando el usuario envía el formulario:

1. **Django recibe el POST** con los datos del formulario
2. **form.is_valid()** ejecuta todas las validaciones:
   - Validaciones de campo (max_length, blank, null)
   - Validadores de formato (EmailValidator)
   - Validaciones personalizadas del modelo
3. **Si hay errores:**
   - El formulario se vuelve a renderizar
   - Se muestran mensajes de error personalizados
   - Los valores válidos se mantienen en los campos
   - Los campos inválidos se marcan con borde rojo
4. **Si es válido:**
   - Se guarda en la base de datos
   - Se envía email de notificación
   - Se redirige al usuario con mensaje de éxito

---

## Mensajes de Error en la Interfaz

### Estructura de Alertas

#### Alert de error general (rojo)
Se muestra si hay errores no asociados a campos específicos:

```html
<div class="alert alert-danger">
    Por favor, corrija los siguientes errores:
    [errores generales]
</div>
```

#### Alert de aviso (amarillo)
Se muestra si hay errores en campos específicos:

```html
<div class="alert alert-warning">
    Atención: Por favor, revise los campos marcados en rojo y corrija los errores.
</div>
```

#### Errores por campo (debajo de cada input)
Crispy forms renderiza automáticamente los errores debajo de cada campo con:
- Texto en rojo
- Clase `invalid-feedback`
- Icono de error (opcional)

---

## Ejemplos de Uso

### Caso 1: Usuario deja todos los campos vacíos

**Mensajes mostrados:**
- Alert amarillo: "Atención: Por favor, revise los campos marcados en rojo..."
- Campo nombre: "Por favor, ingrese su nombre completo."
- Campo email: "Por favor, ingrese su correo electrónico."
- Campo crucero: "Por favor, seleccione un crucero."
- Campo mensaje: "Por favor, déjenos un mensaje con su consulta."

### Caso 2: Usuario ingresa email inválido

**Mensaje mostrado:**
- Campo email: "Ingrese un correo electrónico válido (ejemplo: usuario@dominio.com)."

### Caso 3: Usuario ingresa nombre de 60 caracteres

**Mensaje mostrado:**
- Campo nombre: "El nombre no puede tener más de 50 caracteres."

### Caso 4: Usuario ingresa todos los datos correctamente

**Resultado:**
- ✅ Formulario se guarda
- ✅ Se envía email de notificación al administrador
- ✅ Usuario redirigido a página de inicio
- ✅ Mensaje de éxito: "Thank you, [nombre]! We will email you when we have more information about [crucero]!"

---

## Tests de Validación

El proyecto incluye **9 tests automatizados** que verifican:

1. ✅ Campo nombre no puede estar vacío
2. ✅ Campo nombre respeta max_length de 50
3. ✅ Campo email valida formato correcto
4. ✅ Campo email acepta formatos válidos
5. ✅ Campo email rechaza formatos inválidos
6. ✅ Campo notes no puede estar vacío
7. ✅ Campo notes respeta max_length de 2000
8. ✅ Campo cruise es obligatorio
9. ✅ Datos válidos se guardan correctamente

**Ubicación de los tests:**  
`relecloud/tests/test_info_request_validation.py`

**Ejecutar tests:**
```bash
python manage.py test relecloud.tests.test_info_request_validation
```

---

## Accesibilidad

Las validaciones están diseñadas pensando en accesibilidad:

- **`role="alert"`** en mensajes de error para lectores de pantalla
- **Etiquetas claras** con `verbose_name`
- **Textos de ayuda** con `help_text` para guiar al usuario
- **Mensajes descriptivos** que explican el problema
- **Indicadores visuales** (colores, iconos) y textuales

---

## Mejores Prácticas Implementadas

1. ✅ **Mensajes en español claro** para usuarios hispanohablantes
2. ✅ **Mensajes orientados a la acción** ("Por favor, ingrese..." vs "Este campo es requerido")
3. ✅ **Ejemplos en mensajes de error** (ej: "ejemplo: usuario@dominio.com")
4. ✅ **Validación en el servidor** para seguridad
5. ✅ **Preservación de datos válidos** al re-renderizar el formulario
6. ✅ **Indicadores visuales y textuales** para todos los errores
7. ✅ **Tests automatizados** para garantizar funcionamiento correcto

---

## Tecnologías Utilizadas

- **Django 3.1.7** - Framework web
- **django-crispy-forms** - Renderizado de formularios
- **crispy-bootstrap5** - Estilos Bootstrap 5
- **Bootstrap 5** - Framework CSS
- **Bootstrap Icons** - Iconografía

---

## Mantenimiento

Para modificar los mensajes de error:

1. Editar el modelo en `relecloud/models.py`
2. Actualizar el diccionario `error_messages` de cada campo
3. Ejecutar tests: `python manage.py test relecloud.tests.test_info_request_validation`
4. Verificar visualmente en el navegador

**Nota:** No es necesario crear migraciones al cambiar solo los mensajes de error, `help_text` o `verbose_name`.
