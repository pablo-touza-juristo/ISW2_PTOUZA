
import os
import django
import unicodedata

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from django.core.files import File
from relecloud.models import Destination

def normalize_text(text):
    return ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn').lower()

def populate_images():
    img_dir = 'Imagenes_Destinos'
    
    # Map of specific DB names to fallback categories (if no exact file match found)
    categories = {
        'titan': 'titan.png',
        'venus': 'hot_planet.png',
        'mercurio': 'hot_planet.png',
        'io': 'hot_planet.png',
        'fobos': 'asteroid.png',
        'deimos': 'asteroid.png',
        'ceres': 'icy_body.png', # Dwarf planet
        'vesta': 'icy_body.png', # Asteroid but large
        'pallas': 'icy_body.png',
        'sedna': 'icy_body.png',
        'pluton': 'icy_body.png',
        'triton': 'icy_body.png',
        'caronte': 'icy_body.png',
        'luna europa': 'icy_body.png',
        'europa': 'icy_body.png',
        'ganimedes': 'icy_body.png',
        'calisto': 'icy_body.png',
        'encelado': 'icy_body.png',
    }

    # Get available files
    files = os.listdir(img_dir)
    # Create a normalized map of files: 'cinturon de asteroides' -> 'Cinturon de Asteroides.jpeg'
    file_map = {normalize_text(os.path.splitext(f)[0]): f for f in files}

    destinations = Destination.objects.all()
    print(f"Found {destinations.count()} destinations.")

    for dest in destinations:
        dest_name_norm = normalize_text(dest.name)
        img_filename = None
        
        # 1. Try exact match in file_map
        if dest_name_norm in file_map:
            img_filename = file_map[dest_name_norm]
            print(f"[MATCH] Found exact image for {dest.name}: {img_filename}")
        
        # 2. Try match in categories
        elif dest_name_norm in categories:
            img_filename = categories[dest_name_norm]
            print(f"[CATEGORY] Using {img_filename} for {dest.name}")
            
        # 3. Last Result: Icy Body
        else:
            img_filename = 'icy_body.png'
            print(f"[DEFAULT] Using {img_filename} for {dest.name}")

        if img_filename:
            path = os.path.join(img_dir, img_filename)
            if os.path.exists(path):
                with open(path, 'rb') as f:
                    # Save the image to the model
                    # save=True will commit to DB
                    dest.image.save(img_filename, File(f), save=True)
                    print(f"Saved image for {dest.name}")
            else:
                print(f"ERROR: File not found {path}")
        else:
            print(f"SKIPPING: No image source for {dest.name}")

if __name__ == '__main__':
    populate_images()
