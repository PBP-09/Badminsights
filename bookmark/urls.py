from django.urls import path
from . import views

app_name = 'bookmark'

urlpatterns = [
    path('favorites/', views.show_favorites, name='show_favorites'),
    path('ajax/toggle_favorite/', views.toggle_favorite_ajax, name='toggle_favorite_ajax'),
]
