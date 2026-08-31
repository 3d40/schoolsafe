from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    # Login/Logout
    path('login/', views.custom_login, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    
    # Registrasi
    path('register/', views.register, name='register'),
    
    # Profil
    path('profile/', views.profile, name='profile'),
]