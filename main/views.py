from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import datetime
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Player
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

@login_required(login_url='/login')
def show_main(request):
    filter_type = request.GET.get("filter", "all")  # default 'all'

    if filter_type == "all":
        players = Player.objects.all()
    else:
        players = Player.objects.filter(user=request.user)

    context = {
        'name': request.user.username,
        'players': players,
        'last_login': request.COOKIES.get('last_login', 'Never')
    }
    return render(request, "main.html", context)

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
            response = HttpResponseRedirect(reverse("main:show_main"))
            response.set_cookie('last_login', str(datetime.datetime.now()))
            return response

    else:
        form = AuthenticationForm(request)
    context = {'form': form}
    return render(request, 'login.html', context)

def logout_user(request):
    logout(request)
    response = HttpResponseRedirect(reverse('main:login'))
    response.delete_cookie('last_login')
    return response
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



