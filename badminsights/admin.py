from django.contrib import admin
from django.contrib.auth.models import User, Group
from modules.smash_talk.models import Post, Comment

# Unregister default models
admin.site.unregister(User)
admin.site.unregister(Group)

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'created_at', 'total_likes', 'total_comments']
    list_filter = ['category', 'created_at']
    search_fields = ['title', 'content', 'author__username']
    readonly_fields = ['created_at', 'updated_at', 'views']
    
    fieldsets = (
        ('Informasi Postingan', {
            'fields': ('title', 'author', 'category', 'content')
        }),
        ('Statistik', {
            'fields': ('likes', 'views', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'post', 'created_at', 'total_likes']
    list_filter = ['created_at']
    search_fields = ['content', 'author__username', 'post__title']
    readonly_fields = ['created_at', 'updated_at']

class CustomAdminSite(admin.AdminSite):
    site_header = "🏸 Badminsights Administration"
    site_title = "Badminsights Admin Portal"
    index_title = "Selamat Datang di Portal Admin Badminsights"

# Replace default admin
custom_admin_site = CustomAdminSite(name='custom_admin')
custom_admin_site.register(Post, PostAdmin)
custom_admin_site.register(Comment, CommentAdmin)