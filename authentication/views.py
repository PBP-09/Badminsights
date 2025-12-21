import json
from django.shortcuts import render
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')

            user = authenticate(username=username, password=password)
            
            if user is not None:
                if user.is_active:
                    auth_login(request, user)
                    return JsonResponse({
                        "username": user.username,
                        "status": True, # Boolean
                        "message": "Login successful!"
                    }, status=200)
                else:
                    return JsonResponse({
                        "status": False,
                        "message": "Akun belum aktif."
                    }, status=401)
            else:
                return JsonResponse({
                    "status": False,
                    "message": "Username atau password salah."
                }, status=401)
        except Exception as e:
             return JsonResponse({
                "status": False,
                "message": "Terjadi kesalahan pada server."
            }, status=500)
    
    return JsonResponse({"status": False, "message": "Method not allowed"}, status=405)


@csrf_exempt
def register(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password') # Sesuaikan dengan Flutter yang kirim 'password'

            # Validasi input kosong
            if not username or not password:
                return JsonResponse({
                    "status": False,
                    "message": "Username dan Password tidak boleh kosong."
                }, status=400)
            
            # Cek apakah username sudah ada
            if User.objects.filter(username=username).exists():
                return JsonResponse({
                    "status": False,
                    "message": "Username sudah digunakan."
                }, status=400)
            
            # Buat user baru
            user = User.objects.create_user(username=username, password=password)
            user.save()
            
            return JsonResponse({
                "username": user.username,
                "status": True, # UBAH JADI BOOLEAN (biar Flutter ngerti)
                "message": "Akun berhasil dibuat!"
            }, status=200)

        except Exception as e:
            return JsonResponse({
                "status": False,
                "message": str(e)
            }, status=500)
    
    return JsonResponse({
        "status": False,
        "message": "Invalid request method."
    }, status=400)

@csrf_exempt
def logout(request):
    username = request.user.username
    try:
        auth_logout(request)
        return JsonResponse({
            "username": username,
            "status": True,
            "message": "Logged out successfully!"
        }, status=200)
    except:
        return JsonResponse({
            "status": False,
            "message": "Logout failed."
        }, status=401)