from django.urls import path
from smash_talk.views import forum_list,post_detail,create_post,add_comment,like_post,like_comment,delete_post,delete_comment,get_posts_ajax, create_post_ajax, api_post_detail, api_create_post,api_post_list,  api_toggle_like_post, api_add_comment, api_get_comments,show_json,show_json_by_id

app_name = 'smash_talk'


urlpatterns = [
# --- JALUR WEB (Hanya untuk Browser/Template HTML) ---
    path('', forum_list, name='forum_list'),
    path('post/<int:pk>/', post_detail, name='post_detail'),
    path('create/', create_post, name='create_post'),
    path('post/<int:pk>/comment/', add_comment, name='add_comment'),
    path('post/<int:pk>/like/', like_post, name='like_post'),
    path('comment/<int:pk>/like/', like_comment, name='like_comment'),
    path('post/<int:pk>/delete/', delete_post, name='delete_post'),
    path('comment/<int:pk>/delete/', delete_comment, name='delete_comment'),
    path('json/', show_json, name='show_json'), 
    path('json/<int:id>/', show_json_by_id, name='show_json_by_id'),

    # --- JALUR FLUTTER (Hanya untuk kirim/terima JSON) ---
    # Kita pake prefix 'json/' supaya gak bentrok sama path web
    path('json/', api_post_list, name='api_post_list'),
    path('json/<int:pk>/', api_post_detail, name='api_post_detail'),
    path('create-post-flutter/', api_create_post, name='api_create_post'),
    path('toggle-like-flutter/<int:pk>/', api_toggle_like_post, name='api_toggle_like_post'),
    path('get-comments-flutter/<int:pk>/', api_get_comments, name='api_get_comments'),
    path('add-comment-flutter/<int:pk>/', api_add_comment, name='api_add_comment'),
    path('ajax/posts/', get_posts_ajax, name='get_posts_ajax'),
    path('ajax/create/', create_post_ajax, name='create_post_ajax'),

]