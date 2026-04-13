from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from .forms import UserRegisterForm

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Akun berhasil dibuat! Selamat datang {user.username}')
            return redirect('dashboard')
    else:
        form = UserRegisterForm()
    return render(request, 'accounts/register.html', {'form': form})