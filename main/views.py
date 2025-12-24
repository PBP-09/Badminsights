from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import datetime
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from .models import Player
from django.shortcuts import get_object_or_404, redirect, render
from main.models import Player
from main.forms import PlayerForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.core import serializers
from django.contrib import messages
from bookmark.models import Bookmark
from django_countries import countries as all_countries_lookup

def register(request):
    form = UserCreationForm()

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account has been successfully created!')
            return redirect('main:login')
    context = {'form':form}
    return render(request, 'register.html', context)\
    
def login_user(request):
   if request.method == 'POST':
      form = AuthenticationForm(data=request.POST)

      if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('main:main_page')

   else:
      form = AuthenticationForm(request)
   context = {'form': form}
   return render(request, 'login.html', context)

def logout_user(request):
    logout(request)
    response = HttpResponseRedirect(reverse('main:login'))
    response.delete_cookie('last_login')
    return response
   

def is_staff_user(user):
    return user.is_staff


def main_page(request):
    featured_player = Player.objects.filter(is_featured=True).first()

    context = {
        'featured_player' : featured_player
    }

    return render(request, "main.html", context)

def show_main(request):
    category_filter = request.GET.get('category', '')
    country_filter = request.GET.get('country', '')

    player_list = Player.objects.all()

    if category_filter:
        player_list = player_list.filter(category=category_filter)
    
    if country_filter:
        player_list = player_list.filter(country=country_filter)

    categories = Player.CATEGORY_CHOICES
    used_country_codes = Player.objects.values_list('country', flat=True).distinct()

    countries_list_unsorted = []
    for code in used_country_codes:
        if code:
            try:
                name = all_countries_lookup.name(code)
                countries_list_unsorted.append((code, name))
            except Exception:
                countries_list_unsorted.append((code, code)) 

    countries = sorted(countries_list_unsorted, key=lambda item: item[1])

    context = {
        'player_list' : player_list,      
        'categories': categories,         
        'countries': countries,           
        'selected_category': category_filter, 
        'selected_country': country_filter,   
        'title': 'Daftar Pemain'          
    }
    
    return render(request, "player_list.html", context)

def register(request):
    form = UserCreationForm()

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account has been successfully created!')
            return redirect('main:login')
    context = {'form': form}
    return render(request, 'register.html', context)

def login_user(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)
            response = HttpResponseRedirect(reverse("main:main_page"))
            return response

    else:
        form = AuthenticationForm(request)
    context = {'form': form}
    return render(request, 'login.html', context)

def logout_user(request):
    if request.method == 'POST':
        logout(request)
        response = HttpResponseRedirect(reverse('main:login'))
        response.delete_cookie('last_login')
        return response
    return HttpResponseRedirect(reverse('main:show_main'))
    
    
@user_passes_test(is_staff_user, login_url='/login/')
def add_player(request):
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'

    if request.method == 'POST':
        form = PlayerForm(request.POST, request.FILES)
        
        if form.is_valid():
            player = form.save()
            
            if is_ajax:
                player_data = {
                    'id': player.id,
                    'name': player.name,
                    'country': player.country.name, 
                    'category': player.get_category_display(),
                    'thumbnail_url': player.thumbnail.url if player.thumbnail else None,
                    'world_rank': player.world_rank,
                    'detail_url': reverse('main:show_player', args=[player.id])
                }
                return JsonResponse({'status': 'success', 'player': player_data})
            else:
                return redirect('main:player_list')
        else:
            if is_ajax:
                return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
            else:
                context = {'form': form, 'title': 'Tambah Pemain Baru'}
                return render(request, "player_form.html", context)
    else:
        form = PlayerForm()
        context = {'form': form, 'title': 'Tambah Pemain Baru'}
        
        if is_ajax:
            return render(request, 'player_form_modal.html', context)
        else:
            return render(request, "player_form.html", context)

def show_player(request, id):
    player = get_object_or_404(Player, pk=id)

    is_favorited = False
    if request.user.is_authenticated:
        is_favorited = Bookmark.objects.filter(user=request.user, player=player).exists()

    context = {
        'player' : player,
        'is_favorited': is_favorited 
    }

    return render(request, "player_details.html", context)

@login_required(login_url='/login/')
def edit_player(request, id):
    player = get_object_or_404(Player, pk=id)
    form = PlayerForm(request.POST or None, instance=player)

    if form.is_valid() and request.method == "POST":
        form.save()
        return redirect('main:show_player', id=id)

    context = {'form': form, 'title': f'Edit {player.name}'} 
    
    return render(request, "player_form.html", context)

def show_xml(request):
    player_list = Player.objects.all()
    xml_data = serializers.serialize("xml", player_list)
    return HttpResponse(xml_data, content_type="application/xml")

def show_json(request):
    player_list = Player.objects.all().values()
    return JsonResponse(list(player_list), safe=False)

def show_json_by_id(request, player_id):
    player = Player.objects.filter(pk=player_id).values()
    if player.exists():
        return JsonResponse(player[0], safe=False)
    
    return JsonResponse({"message": "Not Found"}, status=404)

def show_xml_by_id(request, player_id):
    try: 
        player = Player.objects.filter(pk=player_id)
        xml_data = serializers.serialize("xml", player)
        return HttpResponse(xml_data, content_type="application/xml")
    except Player.DoesNotExist:
        return HttpResponse(status=404)


def api_player_list(request):
    players = Player.objects.all()[:5]
    
    data = []
    for p in players:
        thumbnail_url = ""
        
        try:
            if p.thumbnail:
              
                val = str(p.thumbnail)
                
                # 1. Kalau link dari internet (https://...), pakai langsung
                if val.startswith('http'):
                    thumbnail_url = val
                # 2. Kalau file upload lokal, bikin absolute URL
                elif hasattr(p.thumbnail, 'url'):
                    thumbnail_url = request.build_absolute_uri(p.thumbnail.url)
                # 3. Fallback
                else:
                    thumbnail_url = val
        except Exception as e:
            print(f"Error getting image for {p.name}: {e}")
            thumbnail_url = ""
        # -------------------------------------

        rank_display = f"Rank: {p.world_rank}" if p.world_rank else "Unranked"

        data.append({
            "name": p.name,
            "category": p.get_category_display(),
            "rank": rank_display,
            "thumbnail": thumbnail_url, 
        })
        
    return JsonResponse(data, safe=False)