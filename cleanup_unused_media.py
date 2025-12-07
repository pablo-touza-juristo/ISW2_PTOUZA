
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from relecloud.models import Destination
from django.conf import settings

def cleanup_unused_images():
    # 1. Get all image paths currently in use by the DB
    used_images = set()
    for dest in Destination.objects.all():
        if dest.image:
            # dest.image.name gives the relative path like 'destinations/Luna.jpeg'
            # We want the basename or the full path to compare
            full_path = dest.image.path
            used_images.add(os.path.normpath(full_path))
            print(f"Keep: {dest.name} -> {full_path}")

    # 2. Iterate through the media/destinations directory
    media_dest_dir = os.path.join(settings.MEDIA_ROOT, 'destinations')
    
    if not os.path.exists(media_dest_dir):
        print(f"Directory {media_dest_dir} does not exist.")
        return

    print("\nScanning directory for unused files...")
    deleted_count = 0
    for filename in os.listdir(media_dest_dir):
        file_path = os.path.join(media_dest_dir, filename)
        if os.path.isfile(file_path):
            norm_path = os.path.normpath(file_path)
            
            if norm_path not in used_images:
                print(f"Deleting unused: {filename}")
                try:
                    os.remove(norm_path)
                    deleted_count += 1
                except Exception as e:
                    print(f"Error deleting {filename}: {e}")
    
    print(f"\nCleanup finished. Deleted {deleted_count} unused files.")

if __name__ == '__main__':
    cleanup_unused_images()
