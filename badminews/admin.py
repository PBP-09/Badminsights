from django.contrib import admin
from .models import News

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'date_published', 'views', 'total_upvotes', 'get_read_count')
    list_filter = ('category', 'date_published', 'author')
    search_fields = ('title', 'content', 'author__username')
    ordering = ('-date_published',)
    readonly_fields = ('views', 'date_published', 'upvotes', 'read_by')

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'content', 'author', 'category', 'image')
        }),
        ('Statistics', {
            'fields': ('views', 'total_upvotes', 'get_read_count'),
            'classes': ('collapse',)
        }),
        ('User Interactions', {
            'fields': ('upvotes', 'read_by'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('date_published',),
            'classes': ('collapse',)
        }),
    )

    def get_read_count(self, obj):
        return obj.read_by.count()
    get_read_count.short_description = 'Read Count'
    get_read_count.admin_order_field = 'read_by__count'
