from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            
            # Opcional: mostrar qué base de datos usará
            db_name = request.session.get('database', 'default')
            if db_name != 'default':
                messages.success(request, f"Acceso a base de datos: {db_name.upper()}")
            
            return redirect('home')
        else:
            messages.error(request, "Usuario o contraseña incorrectos.")
    return render(request, 'auth/login.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')