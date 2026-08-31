from django.shortcuts import redirect
from django.urls import reverse

class RoleBasedRedirectMiddleware:
    """
    Middleware untuk mengarahkan pengguna ke dashboard sesuai role-nya
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        # Jika user sudah login dan mencoba akses halaman login
        if request.user.is_authenticated and request.path == reverse('accounts:login'):
            return redirect('dashboard:dashboard')
        return None

class RolePermissionMiddleware:
    """
    Middleware untuk memeriksa izin berdasarkan role
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        # Hanya untuk user yang sudah login
        if request.user.is_authenticated:
            # Dapatkan role user
            try:
                role = request.user.profile.role
            except:
                role = 'siswa'  # Default role

            # Daftar URL yang tidak perlu dicek
            allowed_paths = [
                reverse('accounts:login'),
                reverse('accounts:logout'),
                reverse('home'),
            ]

            # Jika di halaman yang tidak perlu dicek, lanjutkan
            if request.path in allowed_paths:
                return None

            # Cek apakah user memiliki akses ke halaman yang diminta
            # Siswa dan guru hanya bisa mengakses dashboard dan reports mereka sendiri
            if role in ['siswa', 'guru']:
                # URL yang bisa diakses siswa/guru
                student_teacher_paths = [
                    '/dashboard/',
                    '/reports/',
                    '/accounts/profile/',
                ]
                
                # Jika tidak ada di path yang diizinkan, redirect ke dashboard
                if not any(request.path.startswith(path) for path in student_teacher_paths):
                    return redirect('dashboard:dashboard')

        return None