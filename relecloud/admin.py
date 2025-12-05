from django.contrib import admin
from django.utils.html import format_html
from . import models

# Register your models here.
admin.site.register(models.Cruise)
# Destination registered below with decorator
admin.site.register(models.InfoRequest)

@admin.register(models.Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ('name', 'image_preview')
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" />', obj.image.url)
        return "Sin imagen"
    image_preview.short_description = 'Preview'


@admin.register(models.Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'destination', 'rating', 'created_at', 'has_comment')
    list_filter = ('rating', 'created_at', 'destination')
    search_fields = ('user__username', 'destination__name', 'comment')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    
    def has_comment(self, obj):
        return obj.has_comment()
    has_comment.boolean = True
    has_comment.short_description = 'Tiene comentario'
