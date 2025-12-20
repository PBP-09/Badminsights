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
    
@login_required
def show_favorite_json(request):
    favorites = Bookmark.objects.filter(user=request.user)
    data = serializers.serialize("json", favorites)
    return HttpResponse(data, content_type="application/json")