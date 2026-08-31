from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm

def register(request):
    """
    View untuk registrasi pengguna baru
    """
    if request.user.is_authenticated:
        return redirect('dashboard:dashboard')
    
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Akun berhasil dibuat! Selamat datang, {user.username}!')
            return redirect('dashboard:dashboard')
        else:
            messages.error(request, 'Terjadi kesalahan. Silakan periksa kembali form.')
    else:
        form = UserRegisterForm()
    
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def profile(request):
    """
    View untuk melihat dan mengedit profil pengguna
    """
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, instance=request.user.profile)
        
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Profil berhasil diperbarui!')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Terjadi kesalahan. Silakan periksa kembali form.')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    
    context = {
        'u_form': u_form,
        'p_form': p_form,
    }
    return render(request, 'accounts/profile.html', context)

def custom_login(request):
    """
    Custom login view dengan redirect berdasarkan role
    """
    if request.user.is_authenticated:
        return redirect('dashboard:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Selamat datang kembali, {user.username}!')
            return redirect('dashboard:dashboard')
        else:
            messages.error(request, 'Username atau password salah!')
            return render(request, 'accounts/login.html')
    
    return render(request, 'accounts/login.html')

def custom_logout(request):
    """
    Custom logout view
    """
    logout(request)
    messages.info(request, 'Anda telah logout.')
    return redirect('accounts:login')