from django.urls import path
from . import views

app_name = 'bookmark'

urlpatterns = [
    path('favorites/', views.show_favorite, name='show_favorite'),
    path('toggle_favorite_ajax/', views.toggle_favorite_ajax, name='toggle_favorite_ajax'),
]
