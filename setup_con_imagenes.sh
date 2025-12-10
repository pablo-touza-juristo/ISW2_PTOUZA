#!/bin/bash

# Script para cargar datos con imágenes desde Imagenes_Destinos/

echo "🚀 Iniciando carga de datos con imágenes..."

# Activar virtual environment si existe
if [ -d ".venv" ]; then
    echo "✓ Activando entorno virtual..."
    source .venv/bin/activate
fi

# 1. Limpiar base de datos
echo ""
echo "📝 Paso 1: Limpiando base de datos anterior..."
rm -f db.sqlite3
echo "✓ Base de datos limpiada"

# 2. Aplicar migraciones
echo ""
echo "📝 Paso 2: Aplicando migraciones..."
python manage.py migrate
echo "✓ Migraciones aplicadas"

# 3. Cargar destinos
echo ""
echo "📝 Paso 3: Cargando destinos..."
python manage.py loaddata relecloud/fixtures/destinations_con_imagenes.json
echo "✓ Destinos cargados"

# 4. Cargar cruceros
echo ""
echo "📝 Paso 4: Cargando cruceros..."
python manage.py loaddata relecloud/fixtures/cruises_con_imagenes.json
echo "✓ Cruceros cargados"

# 5. Asignar imágenes desde Imagenes_Destinos/
echo ""
echo "📝 Paso 5: Asignando imágenes desde Imagenes_Destinos/..."
python populate_images.py
echo "✓ Imágenes asignadas"

# 6. Crear superusuario si no existe
echo ""
echo "📝 Paso 6: Verificando superusuario..."
python manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@relecloud.com', 'admin123');
    print('✓ Superusuario creado (admin/admin123)');
else:
    print('✓ Superusuario ya existe');
"

echo ""
echo "✅ ¡Todo listo! Base de datos poblada con imágenes."
echo ""
echo "📊 Resumen:"
echo "  - Destinos: Luna, Marte, Júpiter, Saturno, ISS, Cinturón de Asteroides"
echo "  - Cruceros: 6 tours espaciales"
echo "  - Imágenes: Cargadas desde Imagenes_Destinos/"
echo ""
echo "🌐 Para iniciar el servidor:"
echo "  python manage.py runserver"
echo ""
echo "🔐 Admin: http://127.0.0.1:8000/admin"
echo "  Usuario: admin"
echo "  Contraseña: admin123"
