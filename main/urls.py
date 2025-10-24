from django.urls import path
from main.views import main_page, show_main, add_player, show_player, toggle_favorite, show_xml, show_json, show_json_by_id, show_xml_by_id, register, login_user, logout_user, edit_player

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
    path('xml/', show_xml, name='show_xml'),
    path('xml/<str:player_id>/', show_xml_by_id, name='show_xml_by_id'),
    path('json/<str:player_id>/', show_json_by_id, name='show_json_by_id'),
    path('register/', register, name='register'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    path('player/<str:id>/edit/', edit_player, name='edit_player'),
]