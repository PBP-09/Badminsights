from django.urls import path
from . import views

app_name = 'badminews'

urlpatterns = [
    path('', views.news_list, name='news_list'),
    path('<int:pk>/', views.news_detail, name='news_detail'),
    path('add/', views.add_news, name='add_news'),
    path('json/', views.news_json, name='news_json'),
]