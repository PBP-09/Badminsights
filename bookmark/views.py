from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from main.models import Player  
from django.contrib.auth.decorators import login_required
from .models import Bookmark

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