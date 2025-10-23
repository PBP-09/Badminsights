from django.urls import path
from main.views import show_main, register, login_user, logout_user
from main.views import main_page, show_main, add_player, show_player, toggle_favorite

app_name = 'main'

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    path('', main_page, name='main_page'),
    path('players/', show_main, name='player_list'),
    path('add/', add_player, name='add_player'),
    path('player/<str:id>/', show_player, name='show_player'),
    path('player/<str:id>/favorite/', toggle_favorite, name='toggle_favorite'),
]