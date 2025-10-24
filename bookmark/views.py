from django.shortcuts import render
from django.http import JsonResponse
from main.models import Player
from django.contrib.auth.decorators import login_required
from .models import Bookmark

# Create your views here.
@login_required(login_url='/login/')
def show_favorite(request):
    favorites = Bookmark.objects.filter(user=request.user)
    
    context = {
        'favorites': favorites
    }
    return render(request, 'bookmark/show_favorite.html', context)

@login_required
def toggle_favorite_ajax(request):
    if request.method == "POST":
        player_id = request.POST.get("player_id")
        player = Player.objects.get(id=player_id)
        bookmark, created = Bookmark.objects.get_or_create(user=request.user, player=player)

        if not created:
            # Sudah ada → hapus
            bookmark.delete()
            return JsonResponse({"status": "removed"})
        else:
            # Belum ada → tambah
            return JsonResponse({"status": "added"})

    return JsonResponse({"error": "Invalid request"}, status=400)