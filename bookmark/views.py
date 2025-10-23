from django.shortcuts import render
from .models import Bookmark
# Create your views here.

def show_favorite(request):
    if request.user.is_authenticated:
        favorites = Bookmark.objects.filter(user=request.user)
    else:
        favorites = []

    context = {
        'favorites': favorites
    }
    
    return render(request, 'bookmark/show_favorite.html', context)
