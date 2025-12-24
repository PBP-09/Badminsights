from django.urls import path
from bookmark.views import show_favorites, toggle_favorite_ajax, show_json, create_bookmark_flutter # <--- Tambah import show_json

app_name = 'bookmark'

urlpatterns = [
    path('', show_favorites, name='show_favorites'),
    path('toggle/', toggle_favorite_ajax, name='toggle_favorite_ajax'),
    path('json/', show_json, name='show_json'),
    path('bookmark/add-flutter/', create_bookmark_flutter, name='create_bookmark_flutter'),  # Contoh endpoint untuk Flutter
]