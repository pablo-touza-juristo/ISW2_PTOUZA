# 🗄️ Uso de SQLite y Carga de Datos

## ✅ Configuración Actual

El proyecto está configurado para usar **SQLite** tanto en desarrollo como en producción.

### **Base de Datos:**
- **Motor:** SQLite
- **Archivo:** `db.sqlite3` (en la raíz del proyecto)
- **Ventajas:** 
  - ✅ No requiere servidor de base de datos
  - ✅ Fácil de usar y configurar
  - ✅ Perfecto para desarrollo y proyectos pequeños
  - ✅ Los datos persisten entre deploys

---

## 📦 Carga de Datos Iniciales

### **Opción 1: Usar el Script de Carga de Datos** (RECOMENDADO)

El proyecto incluye un script que carga datos de prueba con destinos, cruceros y reviews:

```bash
# Activar entorno virtual
source .venv/bin/activate

# Ejecutar script de carga de datos
python load_test_data.py
```

**Datos que se cargan:**
- ✅ 18 destinos (Marte, Luna Europa, Titán, etc.)
- ✅ Reviews con diferentes puntuaciones
- ✅ Usuarios de prueba
- ✅ Los destinos se ordenan por popularidad

---

### **Opción 2: Usar Fixtures (Datos Mínimos)**

Si solo quieres los destinos y cruceros básicos sin reviews:

```bash
# Cargar destinos
python manage.py loaddata relecloud/fixtures/destinations.json

# Cargar cruceros
python manage.py loaddata relecloud/fixtures/cruises.json
```

**Datos que se cargan:**
- ✅ 6 destinos básicos (Moon, Mars, Europa, Titan, Enceladus, Pluto)
- ✅ 6 cruceros con diferentes itinerarios

---

### **Opción 3: Crear Datos Manualmente (Admin)**

1. Ejecuta el servidor:
```bash
python manage.py runserver
```

2. Ve al admin de Django: http://localhost:8000/admin

3. Inicia sesión con tu superusuario (créalo si no existe):
```bash
python manage.py createsuperuser
```

4. Crea destinos, cruceros, reviews, etc. desde la interfaz del admin

---

## 🔄 Resetear la Base de Datos

Si quieres empezar desde cero:

```bash
# 1. Borrar la base de datos
rm db.sqlite3

# 2. Ejecutar migraciones
python manage.py migrate

# 3. Crear superusuario
python manage.py createsuperuser

# 4. Cargar datos iniciales (elige una opción)
# Opción A: Script completo con reviews
python load_test_data.py

# Opción B: Solo fixtures básicos
python manage.py loaddata relecloud/fixtures/destinations.json
python manage.py loaddata relecloud/fixtures/cruises.json
```

---

## 🚀 En Producción (Azure)

### **La base de datos SQLite también funciona en Azure:**

1. **El archivo `db.sqlite3` se despliega con el código**
2. **Los datos persisten** entre deploys (se mantienen en `/home/site/wwwroot/`)
3. **No necesitas configurar variables de PostgreSQL**

### **Cargar datos en Azure:**

Después del deploy, conéctate por SSH y ejecuta:

```bash
cd /home/site/wwwroot

# Opción A: Script completo
python load_test_data.py

# Opción B: Fixtures
python manage.py loaddata relecloud/fixtures/destinations.json
python manage.py loaddata relecloud/fixtures/cruises.json

# Crear superusuario
python manage.py createsuperuser
```

---

## 📊 Estructura de Datos

### **Destinos incluidos en fixtures:**

| ID | Nombre | Descripción |
|----|--------|-------------|
| 1 | Moon | Lunar surface exploration, Earth-rise views |
| 2 | Mars | Red Planet, Olympus Mons, Valles Marineris |
| 3 | Europa | Jupiter's ice moon, subsurface ocean |
| 4 | Titan | Saturn's largest moon, methane seas |
| 5 | Enceladus | Ice geysers, water plumes |
| 6 | Pluto | Edge of solar system, heart-shaped glacier |

### **Cruceros incluidos en fixtures:**

| ID | Nombre | Duración | Destinos |
|----|--------|----------|----------|
| 1 | Lunar Gateway Express | 3 días | Moon |
| 2 | Mars Pioneer | 2 semanas | Moon, Mars |
| 3 | Jovian Moons Tour | 3 semanas | Moon, Europa |
| 4 | Saturn Grand Tour | 4 semanas | Moon, Mars, Titan, Enceladus |
| 5 | Outer Solar System | 6 semanas | Todos |
| 6 | Ice Moons Explorer | 3 semanas | Europa, Titan, Enceladus |

---

## ⚠️ Notas Importantes

### **SQLite vs PostgreSQL:**

| Característica | SQLite | PostgreSQL |
|----------------|--------|------------|
| **Configuración** | ✅ Ninguna | Servidor, credenciales |
| **Tamaño proyecto** | ✅ Pequeño/Mediano | Grande |
| **Concurrencia** | Limitada | ✅ Alta |
| **Backups** | Copiar archivo | ✅ Herramientas avanzadas |
| **Producción** | ✅ OK para bajo tráfico | ✅ Recomendado para alto tráfico |

### **Para este proyecto (ReleCloud):**
- ✅ SQLite es **suficiente** para desarrollo y producción con bajo tráfico
- ✅ Los datos **persisten** en Azure
- ✅ **Más simple** de mantener
- ✅ **No requiere** configuración adicional

---

## 🆘 Troubleshooting

### ❌ Error: "no such table: relecloud_destination"

**Solución:** No ejecutaste las migraciones
```bash
python manage.py migrate
```

### ❌ Error: "database is locked"

**Solución:** SQLite no permite múltiples escrituras simultáneas
- Cierra otros procesos que usen la BD
- En producción, usa PostgreSQL si tienes mucho tráfico

### ❌ No hay datos en la aplicación

**Solución:** Carga datos iniciales
```bash
python load_test_data.py
```

---

## ✅ Checklist de Setup Completo

- [ ] Base de datos creada (`db.sqlite3` existe)
- [ ] Migraciones ejecutadas (`python manage.py migrate`)
- [ ] Superusuario creado (`python manage.py createsuperuser`)
- [ ] Datos cargados (`python load_test_data.py` o fixtures)
- [ ] Servidor corriendo (`python manage.py runserver`)
- [ ] Admin accesible (http://localhost:8000/admin)
- [ ] Destinos visibles (http://localhost:8000/destinations)

---

## 📚 Comandos Útiles

```bash
# Ver el estado de las migraciones
python manage.py showmigrations

# Crear migraciones si cambias modelos
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Acceder a la shell de Django
python manage.py shell

# Ejecutar consultas SQL directas
python manage.py dbshell

# Ver todas las tablas
.tables

# Salir de dbshell
.quit
```

---

## 🎯 Resumen

1. **SQLite está configurado** y listo para usar
2. **Usa `load_test_data.py`** para cargar datos completos con reviews
3. **O usa fixtures** para datos mínimos sin reviews
4. **En Azure** también usa SQLite, los datos persisten
5. **No necesitas PostgreSQL** para este proyecto
