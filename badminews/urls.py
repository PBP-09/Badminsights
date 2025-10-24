from django.urls import path
from . import views

app_name = 'badminews'

urlpatterns = [
    path('', views.news_list, name='news_list'),
    path('<int:pk>/', views.news_detail, name='news_detail'),
    path('<int:pk>/upvote/', views.upvote_news, name='upvote_news'),
    path('<int:pk>/edit/', views.edit_news, name='edit_news'),
    path('<int:pk>/delete/', views.delete_news, name='delete_news'),
    path('add/', views.add_news, name='add_news'),
    path('create-ajax/', views.create_news_ajax, name='create_news_ajax'),
    path('json/', views.news_json, name='news_json'),
]