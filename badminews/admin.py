from django.contrib import admin
from .models import News

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'date_published', 'views', 'total_upvotes')
    list_filter = ('category', 'date_published', 'author')
    search_fields = ('title', 'content', 'author__username')
    ordering = ('-date_published',)
    readonly_fields = ('views', 'date_published')

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'content', 'author', 'category', 'image')
        }),
        ('Statistics', {
            'fields': ('views', 'upvotes'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('date_published',),
            'classes': ('collapse',)
        }),
    )
