import json
from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from main.models import Player  
from django.contrib.auth.decorators import login_required
from .models import Bookmark
from django.core import serializers
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.html import strip_tags

@login_required(login_url='/login/')
def show_favorites(request): 
    favorites = Bookmark.objects.filter(user=request.user)
    
    context = {
        'favorites': favorites
    }
    
    return render(request, 'favorite_list.html', context)


@login_required
def toggle_favorite_ajax(request):
    if not request.method == "POST":
        return JsonResponse({"error": "Metode tidak diizinkan"}, status=405)

    try:
        player_id = request.POST.get("player_id")
        
        if not player_id:
            return JsonResponse({"error": "Player ID tidak ada"}, status=400)
        
        player = get_object_or_404(Player, id=player_id)

        bookmark, created = Bookmark.objects.get_or_create(user=request.user, player=player)

        if not created:
            bookmark.delete()
            return JsonResponse({"status": "removed", "is_favorited": False})
        else:
            return JsonResponse({"status": "added", "is_favorited": True})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    # --- TAMBAHKAN INI DI bookmark/views.py ---

@login_required
def show_json(request):
    # Ambil semua bookmark milik user yang sedang login
    bookmarks = Bookmark.objects.filter(user=request.user)
    
    data = []
    for b in bookmarks:
        # Ambil data player terkait
        player = b.player
        
        # Logika Gambar (Biar aman kayak di main menu tadi)
        thumbnail_url = ""
        try:
            if player.thumbnail:
                val = str(player.thumbnail)
                if val.startswith('http'):
                    thumbnail_url = val
                else:
                    thumbnail_url = request.build_absolute_uri(player.thumbnail.url)
        except:
            thumbnail_url = ""

        # Susun data JSON yang dibutuhkan Flutter
        data.append({
            "id": b.id,
            "player_id": player.id,
            "player_name": player.name,
            "category": player.get_category_display(), # Biar muncul "Men's Singles"
            "player_image": thumbnail_url,
        })
        
    return JsonResponse(data, safe=False)

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
import json

@csrf_exempt
def create_bookmark_flutter(request):
    if request.method != "POST":
        return JsonResponse({"status": "error"}, status=401)

    try:
        data = json.loads(request.body)
        player_id = data.get("player_id")

        if not player_id:
            return JsonResponse(
                {"status": "error", "message": "player_id is required"},
                status=400
            )

        user = request.user
        player = get_object_or_404(Player, id=player_id)

        bookmark, created = Bookmark.objects.get_or_create(
            user=user,
            player=player
        )

        if not created:
            return JsonResponse(
                {"status": "error", "message": "Already bookmarked"},
                status=409
            )

        return JsonResponse(
            {"status": "success", "message": "Bookmark added"},
            status=200
        )

    except Exception as e:
        return JsonResponse(
            {"status": "error", "message": str(e)},
            status=500
        )
