from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.Cruise)
admin.site.register(models.Destination)
admin.site.register(models.InfoRequest)


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
