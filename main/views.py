from django.shortcuts import get_object_or_404, redirect, render
from main.models import Player
from main.forms import PlayerForm
from django.contrib.auth.decorators import login_required, user_passes_test

def is_staff_user(user):
    return user.is_staff

def main_page(request):
    featured_player = Player.objects.filter(is_featured=True).first()

    context = {
        'featured_player' : featured_player
    }

    return render(request, "main.html", context)

def show_main(request):
    player_list = Player.objects.all()

    context = {
        'name' : 'badminsights user',
        'player_list' : player_list,
    }
    return render(request, "player_list.html", context)
    
@user_passes_test(is_staff_user, login_url='/login/')
def add_player(request):
    form = PlayerForm(request.POST or None)

    if form.is_valid() and request.method == "POST":
        form.save()
        return redirect('main:player_list')

    context = {'form': form, 'title' : 'Tambah Player Baru'}
    return render(request, "player_form.html", context)

def show_player(request, id):
    player = get_object_or_404(Player, pk=id)

    context = {
        'player' : player
    }

    return render(request, "player_details.html", context)

@user_passes_test(is_staff_user, login_url='/login/')
def edit_player(request, id):
    player = get_object_or_404(Player, pk=id)
    
    form = PlayerForm(request.POST or None, instance=player)

    if form.is_valid() and request.method == "POST":
        form.save()
        return redirect('main:show_player', id=id)

    context = {'form': form, 'title': f'Edit {player.name}'}
    return render(request, "player_form.html", context)

@login_required(login_url='/login/')
def toggle_favorite(request, player_id):
    pass



