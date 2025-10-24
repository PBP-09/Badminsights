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
from django.http import HttpResponse
from django.core import serializers
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

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
    return redirect('main:login')

def is_staff_user(user):
    return user.is_staff


@login_required(login_url='/login/')
def main_page(request):
    featured_player = Player.objects.filter(is_featured=True).first()

    context = {
        'featured_player' : featured_player
    }

    return render(request, "main.html", context)

@login_required(login_url='/login/')
def show_main(request):
    player_list = Player.objects.all()

    context = {
        'name' : 'badminsights user',
        'player_list' : player_list,
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

@login_required(login_url='/login/')
# @user_passes_test(is_staff_user, login_url='/login/')
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


'''
ini penting gak sih??? perlu gak???
'''

def show_xml(request):
    player_list = Player.objects.all()
    xml_data = serializers.serialize("xml", player_list)
    return HttpResponse(xml_data, content_type="application/xml")

def show_json(request):
    player_list = Player.objects.all()
    json_data = serializers.serialize("json", player_list)
    return HttpResponse(json_data, content_type="application/json")

def show_xml_by_id(request, player_id):
    try: 
        player = Player.objects.filter(pk=player_id)
        xml_data = serializers.serialize("xml", player)
        return HttpResponse(xml_data, content_type="application/xml")
    except Player.DoesNotExist:
        return HttpResponse(status=404)

def show_json_by_id(request, player_id):
    try:
        player = Player.objects.get(pk=player_id)
        json_data = serializers.serialize("json", [player])
        return HttpResponse(json_data, content_type="application/json")
    except Player.DoesNotExist:
        return HttpResponse(status=404)