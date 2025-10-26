# smash_talk/admin.py
from django.contrib import admin
from django.db.models import Count
from .models import Post, Comment, UserProfile


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'like_count_admin', 'created_at')
    list_filter = ('category',  'created_at', 'author')
    search_fields = ('title', 'content', 'author__username')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # annotate jumlah like supaya bisa di-order di admin
        return qs.annotate(_like_count=Count('likes'))

    def like_count_admin(self, obj):
        # gunakan annotated value jika tersedia (lebih efisien)
        return getattr(obj, '_like_count', obj.likes.count())
    like_count_admin.admin_order_field = '_like_count'
    like_count_admin.short_description = 'Likes'

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'created_at')
    search_fields = ('content', 'author__username')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')
    list_filter = ('role',)
