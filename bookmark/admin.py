from django.contrib import admin
from .models import Bookmark

@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    
    list_display = ('user', 'player', 'created_at')
    
    search_fields = ('user__username', 'player__name')
    
    list_filter = ('created_at',)
    
    autocomplete_fields = ('user', 'player')