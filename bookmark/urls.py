from django.urls import path
from . import views

app_name = 'bookmark'

urlpatterns = [
    path('favorites/', views.show_favorite, name='show_favorite'),
]
