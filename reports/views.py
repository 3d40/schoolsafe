from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.utils import timezone
from .models import FacilityReport, RepairHistory
from .forms import ReportForm, ReportUpdateStatusForm
from accounts.models import Profile

@login_required
def create_report(request):
    """
    View untuk membuat laporan baru
    """
    # Cek role - hanya siswa dan guru yang bisa membuat laporan
    if request.user.profile.role not in ['siswa', 'guru']:
        messages.warning(request, 'Hanya siswa dan guru yang dapat membuat laporan.')
        return redirect('dashboard:dashboard')
    
    if request.method == 'POST':
        form = ReportForm(request.POST, request.FILES)
        if form.is_valid():
            # Simpan laporan
            report = form.save(commit=False)
            report.reporter = request.user
            report.save()
            
            # Buat riwayat awal
            RepairHistory.objects.create(
                report=report,
                changed_by=request.user,
                old_status='waiting',
                new_status='waiting',
                note=f'Laporan dibuat oleh {request.user.get_full_name()}'
            )
            
            messages.success(
                request, 
                f'✅ Laporan berhasil dikirim! Nomor laporan: {report.report_number}'
            )
            return redirect('reports:detail', pk=report.id)
        else:
            messages.error(request, '❌ Terjadi kesalahan. Silakan periksa kembali form.')
    else:
        form = ReportForm()
    
    # Ambil data untuk info tambahan
    user = request.user
    context = {
        'form': form,
        'user_full_name': user.get_full_name(),
        'user_role': user.profile.get_role_display(),
        'today': timezone.now(),
    }
    return render(request, 'reports/create_report.html', context)

@login_required
def report_list(request):
    """
    View untuk daftar laporan
    """
    user = request.user
    role = user.profile.role
    
    # Tentukan query berdasarkan role
    if role == 'admin':
        reports = FacilityReport.objects.all()
    else:
        # Siswa/guru hanya melihat laporan mereka
        reports = FacilityReport.objects.filter(reporter=user)
    
    # Filter
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
            Q(description__icontains=search_query)
        )
    
    # Urutkan berdasarkan prioritas dan terbaru
    reports = reports.order_by('-priority_score', '-created_at')
    
    # Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(reports, 10)  # 10 laporan per halaman
    
    try:
        reports_page = paginator.page(page)
    except PageNotAnInteger:
        reports_page = paginator.page(1)
    except EmptyPage:
        reports_page = paginator.page(paginator.num_pages)
    
    context = {
        'reports': reports_page,
        'status_filter': status_filter,
        'urgency_filter': urgency_filter,
        'search_query': search_query,
        'is_admin': role == 'admin',
    }
    return render(request, 'reports/report_list.html', context)

@login_required
def report_detail(request, pk):
    """
    View untuk detail laporan
    """
    report = get_object_or_404(FacilityReport, pk=pk)
    user = request.user
    
    # Cek akses: admin bisa lihat semua, siswa/guru hanya lihat miliknya
    if user.profile.role == 'admin':
        can_edit = True
    elif report.reporter == user:
        can_edit = False  # User tidak bisa edit status
    else:
        messages.warning(request, 'Anda tidak memiliki akses ke laporan ini.')
        return redirect('dashboard:dashboard')
    
    # Ambil riwayat perbaikan
    history = report.history.all().order_by('created_at')
    
    # Form untuk update status (hanya admin)
    status_form = None
    if user.profile.role == 'admin':
        if request.method == 'POST' and 'update_status' in request.POST:
            status_form = ReportUpdateStatusForm(request.POST, instance=report)
            if status_form.is_valid():
                old_status = report.status
                status_form.save()
                new_status = report.status
                
                # Buat riwayat perubahan
                RepairHistory.objects.create(
                    report=report,
                    changed_by=user,
                    old_status=old_status,
                    new_status=new_status,
                    note=report.admin_note
                )
                
                # Cek apakah laporan selesai
                if new_status == 'completed':
                    messages.success(request, '✅ Laporan telah selesai ditangani!')
                else:
                    messages.success(request, f'✅ Status laporan diperbarui: {report.get_status_display()}')
                
                return redirect('reports:detail', pk=report.id)
        else:
            status_form = ReportUpdateStatusForm(instance=report)
    
    context = {
        'report': report,
        'history': history,
        'can_edit': can_edit,
        'status_form': status_form,
        'is_admin': user.profile.role == 'admin',
    }
    return render(request, 'reports/report_detail.html', context)

@login_required
def delete_report(request, pk):
    """
    View untuk menghapus laporan (hanya admin atau pemilik)
    """
    report = get_object_or_404(FacilityReport, pk=pk)
    user = request.user
    
    # Cek akses
    if user.profile.role != 'admin' and report.reporter != user:
        messages.warning(request, 'Anda tidak memiliki akses untuk menghapus laporan ini.')
        return redirect('dashboard:dashboard')
    
    if request.method == 'POST':
        report_number = report.report_number
        report.delete()
        messages.success(request, f'Laporan {report_number} berhasil dihapus.')
        return redirect('reports:list')
    
    context = {
        'report': report,
    }
    return render(request, 'reports/delete_report.html', context)

@login_required
def my_reports(request):
    """
    View untuk melihat laporan sendiri (redirect ke report_list)
    """
    return redirect('reports:list')