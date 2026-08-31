from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from reports.models import FacilityReport

@login_required
def dashboard(request):
    """
    Dashboard utama berdasarkan role pengguna
    """
    user = request.user
    role = user.profile.role
    
    # Data dasar untuk semua role
    if role == 'admin':
        # Admin melihat semua laporan
        reports = FacilityReport.objects.all()
        total_reports = reports.count()
        waiting_count = reports.filter(status='waiting').count()
        repairing_count = reports.filter(status='repairing').count()
        completed_count = reports.filter(status='completed').count()
        high_urgency_count = reports.filter(urgency='high').count()
        
        # Filter berdasarkan parameter GET
        status_filter = request.GET.get('status')
        urgency_filter = request.GET.get('urgency')
        search_query = request.GET.get('search')
        
        if status_filter:
            reports = reports.filter(status=status_filter)
        if urgency_filter:
            reports = reports.filter(urgency=urgency_filter)
        if search_query:
            reports = reports.filter(
                Q(report_number__icontains=search_query) |
                Q(damage_type__name__icontains=search_query) |
                Q(location__name__icontains=search_query) |
                Q(reporter__username__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        # Urutkan berdasarkan prioritas dan terbaru
        reports = reports.order_by('-priority_score', '-created_at')
        
        context = {
            'role': role,
            'reports': reports[:20],  # Batasi 20 laporan
            'total_reports': total_reports,
            'waiting_count': waiting_count,
            'repairing_count': repairing_count,
            'completed_count': completed_count,
            'high_urgency_count': high_urgency_count,
            'status_filter': status_filter,
            'urgency_filter': urgency_filter,
            'search_query': search_query,
            'is_admin': True,
        }
        return render(request, 'dashboard/admin_dashboard.html', context)
    
    else:
        # Siswa/Guru hanya melihat laporan mereka sendiri
        reports = FacilityReport.objects.filter(reporter=user)
        total_reports = reports.count()
        waiting_count = reports.filter(status='waiting').count()
        repairing_count = reports.filter(status='repairing').count()
        completed_count = reports.filter(status='completed').count()
        
        context = {
            'role': role,
            'reports': reports.order_by('-created_at')[:20],
            'total_reports': total_reports,
            'waiting_count': waiting_count,
            'repairing_count': repairing_count,
            'completed_count': completed_count,
            'is_student': role == 'siswa',
            'is_teacher': role == 'guru',
        }
        return render(request, 'dashboard/student_dashboard.html', context)

@login_required
def dashboard_redirect(request):
    """
    Redirect ke dashboard yang sesuai
    """
    return redirect('dashboard:dashboard')