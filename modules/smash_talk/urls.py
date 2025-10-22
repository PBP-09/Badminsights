from django.urls import path
from . import views

app_name = 'smash_talk'

urlpatterns = [
    path('', views.forum_list, name='forum_list'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('create/', views.create_post, name='create_post'),
    path('post/<int:pk>/comment/', views.add_comment, name='add_comment'),
    path('post/<int:pk>/like/', views.like_post, name='like_post'),
    path('comment/<int:pk>/like/', views.like_comment, name='like_comment'),
    path('post/<int:pk>/delete/', views.delete_post, name='delete_post'),
    path('comment/<int:pk>/delete/', views.delete_comment, name='delete_comment'),
]