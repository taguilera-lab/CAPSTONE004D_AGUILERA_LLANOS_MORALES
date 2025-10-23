from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import LoginForm
from documents.models import FlotaUser

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Bienvenido, {username}!")
                # Redirigir según rol
                try:
                    flota_user = user.flotauser
                    role_name = flota_user.role.name
                    if role_name == 'Jefe de Flota':
                        return redirect('jefe_flota_dashboard')
                    elif role_name == 'Mecánico':
                        return redirect('mecanico_dashboard')
                    elif role_name == 'Vendedor':
                        return redirect('vendedor_dashboard')
                    elif role_name == 'Guardia':
                        return redirect('guardia_dashboard')
                    elif role_name == 'Bodeguero':
                        return redirect('bodeguero_dashboard')
                    elif role_name == 'Supervisor':
                        return redirect('supervisor_dashboard')
                    elif role_name == 'Jefe de taller':
                        return redirect('jefe_taller_dashboard')
                    elif role_name == 'Recepcionista de Vehículos':
                        return redirect('recepcionista_dashboard')
                    else:
                        return redirect('home')
                except FlotaUser.DoesNotExist:
                    messages.error(request, "Usuario no tiene perfil de FlotaUser.")
                    return redirect('login')
            else:
                messages.error(request, "Usuario o contraseña incorrectos.")
        else:
            messages.error(request, "Formulario inválido.")
    else:
        form = LoginForm()
    return render(request, 'login/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "Has cerrado sesión.")
    return redirect('login')

# Dashboards placeholders (redirigir a vistas reales)
@login_required
def jefe_flota_dashboard(request):
    return render(request, 'login/dashboard.html', {'role': 'Jefe de Flota'})

@login_required
def mecanico_dashboard(request):
    return render(request, 'login/dashboard.html', {'role': 'Mecánico'})

@login_required
def vendedor_dashboard(request):
    return render(request, 'login/dashboard.html', {'role': 'Vendedor'})

@login_required
def guardia_dashboard(request):
    return render(request, 'login/dashboard.html', {'role': 'Guardia'})

@login_required
def bodeguero_dashboard(request):
    return render(request, 'login/dashboard.html', {'role': 'Bodeguero'})

@login_required
def supervisor_dashboard(request):
    return render(request, 'login/dashboard.html', {'role': 'Supervisor'})

@login_required
def jefe_taller_dashboard(request):
    return render(request, 'login/dashboard.html', {'role': 'Jefe de taller'})

@login_required
def recepcionista_dashboard(request):
    return render(request, 'login/dashboard.html', {'role': 'Recepcionista de Vehículos'})
