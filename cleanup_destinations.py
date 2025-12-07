
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from relecloud.models import Destination

def cleanup_destinations():
    # Names to keep (exact matches from previous output)
    keep_names = [
        'Cinturón de Asteroides',
        'Estación Espacial Internacional',
        'Júpiter',
        'Luna',
        'Marte',
        'Saturno'
    ]
    
    # Also handle normalized or alternate versions just in case, but let's try to match loosely or exclude based on ID/Name
    # Let's simple iterate and delete if not in keywords
    
    keywords = ['Cintur', 'Estaci', 'Jpiter', 'Jupiter', 'Luna', 'Marte', 'Saturno']
    # The names in DB might have accents: 'Cinturón de Asteroides', 'Estación Espacial Internacional', 'Júpiter'
    # Or 'Cinturon de Asteroides' (no accent).
    # Based on previous output: 'Cinturn de Asteroides', 'Estacin...', 'Jpiter' (encoding issues in terminal output)
    # But Python internal strings should be correct.
    
    all_destinations = Destination.objects.all()
    count_deleted = 0
    
    print("Starting cleanup...")
    for dest in all_destinations:
        # Check against allowlist
        # flexible check
        is_allowed = False
        name_lower = dest.name.lower()
        
        if 'cintur' in name_lower and 'asteroide' in name_lower:
            is_allowed = True
        elif 'estaci' in name_lower and 'internacional' in name_lower:
            is_allowed = True
        elif 'jupiter' in name_lower or 'júpiter' in name_lower:
            is_allowed = True
        elif 'luna' in name_lower and 'europa' not in name_lower: # Keep Luna, exclude Luna Europa if it's separate? 
            # User said: "Luna". Did they mean ONLY "Earth's Moon"? 
            # Previous list had "Luna" and "Luna Europa".
            # User said: "Solo tiene que haber ... Luna ...".
            # Usually implies excluding "Luna Europa". I will assume strict compliance.
            if dest.name.strip() == 'Luna':
                is_allowed = True
        elif 'marte' in name_lower:
            is_allowed = True
        elif 'saturno' in name_lower:
            is_allowed = True
            
        if not is_allowed:
            print(f"Deleting: {dest.name}")
            dest.delete()
            count_deleted += 1
        else:
            print(f"Keeping: {dest.name}")

    print(f"Cleanup complete. Deleted {count_deleted} destinations.")

if __name__ == '__main__':
    cleanup_destinations()
