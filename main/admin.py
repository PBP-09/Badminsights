from django.contrib import admin
from .models import Player

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):

    list_display = (
        'name', 
        'country', 
        'category', 
        'world_rank', 
        'status', 
        'is_featured'
    )
    
    list_filter = (
        'category', 
        'status', 
        'is_featured', 
        'country'
    )
    
    search_fields = (
        'name', 
        'country__name' 
    )
    
    list_editable = (
        'world_rank', 
        'status', 
        'is_featured'
    )
    
    fieldsets = (
        ('Informasi Utama', {
            'fields': ('name', 'country', 'date_of_birth', 'thumbnail')
        }),
        ('Detail Olahraga', {
            'fields': ('category', 'world_rank', 'status', 'partner')
        }),
        ('Status & Biografi', {
            'fields': ('bio', 'is_featured')
        }),
    )
    
    autocomplete_fields = ['partner']