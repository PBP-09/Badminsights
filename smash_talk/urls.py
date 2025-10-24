from django.urls import path
from smash_talk.views import forum_list,post_detail,create_post,add_comment,like_post,like_comment,delete_post,delete_comment,get_posts_ajax, create_post_ajax
app_name = 'smash_talk'

urlpatterns = [
    path('', forum_list, name='forum_list'),
    path('post/<int:pk>/', post_detail, name='post_detail'),
    path('create/', create_post, name='create_post'),
    path('post/<int:pk>/comment/', add_comment, name='add_comment'),
    path('post/<int:pk>/like/', like_post, name='like_post'),
    path('comment/<int:pk>/like/', like_comment, name='like_comment'),
    path('post/<int:pk>/delete/', delete_post, name='delete_post'),
    path('comment/<int:pk>/delete/', delete_comment, name='delete_comment'),
     path('ajax/posts/', get_posts_ajax, name='get_posts_ajax'),
    path('ajax/create/', create_post_ajax, name='create_post_ajax'),
]