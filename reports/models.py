from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid

class Location(models.Model):
    """
    Model untuk lokasi fasilitas sekolah
    """
    name = models.CharField('Nama Lokasi', max_length=100)
    description = models.TextField('Deskripsi', blank=True, null=True)
    is_active = models.BooleanField('Aktif', default=True)
    created_at = models.DateTimeField('Tanggal Dibuat', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Lokasi'
        verbose_name_plural = 'Lokasi'
        ordering = ['name']
    
    def __str__(self):
        return self.name

class DamageType(models.Model):
    """
    Model untuk jenis kerusakan
    """
    name = models.CharField('Nama Jenis', max_length=100)
    description = models.TextField('Deskripsi', blank=True, null=True)
    is_active = models.BooleanField('Aktif', default=True)
    created_at = models.DateTimeField('Tanggal Dibuat', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Jenis Kerusakan'
        verbose_name_plural = 'Jenis Kerusakan'
        ordering = ['name']
    
    def __str__(self):
        return self.name

class FacilityReport(models.Model):
    """
    Model utama untuk laporan kerusakan fasilitas
    """
    # Status choices
    STATUS_CHOICES = (
        ('waiting', 'Menunggu'),
        ('repairing', 'Sedang Diperbaiki'),
        ('completed', 'Selesai'),
    )
    
    # Urgency choices
    URGENCY_CHOICES = (
        ('low', 'Rendah'),
        ('medium', 'Sedang'),
        ('high', 'Tinggi'),
    )
    
    # Informasi Laporan
    report_number = models.CharField('Nomor Laporan', max_length=20, unique=True, editable=False)
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports', verbose_name='Pelapor')
    
    # Informasi Kerusakan
    damage_type = models.ForeignKey(DamageType, on_delete=models.CASCADE, related_name='reports', verbose_name='Jenis Kerusakan')
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='reports', verbose_name='Lokasi')
    urgency = models.CharField('Tingkat Urgensi', max_length=10, choices=URGENCY_CHOICES, default='medium')
    description = models.TextField('Keterangan', help_text='Jelaskan kerusakan secara detail')
    photo = models.ImageField('Foto Kerusakan', upload_to='damage_photos/%Y/%m/%d/', blank=True, null=True)
    
    # Status dan Prioritas
    status = models.CharField('Status', max_length=10, choices=STATUS_CHOICES, default='waiting')
    priority_score = models.IntegerField('Skor Prioritas', default=1, editable=False)
    
    # Catatan dan Tanggal
    admin_note = models.TextField('Catatan Petugas', blank=True, null=True)
    created_at = models.DateTimeField('Tanggal Laporan', auto_now_add=True)
    updated_at = models.DateTimeField('Tanggal Diperbarui', auto_now=True)
    completed_at = models.DateTimeField('Tanggal Selesai', blank=True, null=True)
    
    class Meta:
        verbose_name = 'Laporan'
        verbose_name_plural = 'Laporan Kerusakan'
        ordering = ['-priority_score', '-created_at']  # Urutkan berdasarkan prioritas tertinggi dan terbaru
        indexes = [
            models.Index(fields=['status', 'priority_score']),
            models.Index(fields=['urgency', 'status']),
        ]
    
    def __str__(self):
        return f"{self.report_number} - {self.damage_type.name}"
    
    def save(self, *args, **kwargs):
        # Generate nomor laporan otomatis
        if not self.report_number:
            year = timezone.now().strftime('%Y')
            # Ambil jumlah laporan tahun ini
            count = FacilityReport.objects.filter(
                created_at__year=timezone.now().year
            ).count() + 1
            self.report_number = f"SS-{year}-{str(count).zfill(4)}"
        
        # Hitung skor prioritas
        # Algoritma Prioritas:
        # Rendah = 1
        # Sedang = 2
        # Tinggi = 3
        # Laporan dengan urgensi tinggi akan muncul lebih dulu
        urgency_scores = {
            'low': 1,
            'medium': 2,
            'high': 3
        }
        self.priority_score = urgency_scores.get(self.urgency, 1)
        
        # Set completed_at jika status berubah menjadi selesai
        if self.status == 'completed' and not self.completed_at:
            self.completed_at = timezone.now()
        elif self.status != 'completed':
            self.completed_at = None
        
        super().save(*args, **kwargs)
    
    def get_status_badge(self):
        """Mengembalikan class badge untuk status"""
        badges = {
            'waiting': 'badge-waiting',
            'repairing': 'badge-repairing',
            'completed': 'badge-completed'
        }
        return badges.get(self.status, '')
    
    def get_status_icon(self):
        """Mengembalikan icon untuk status"""
        icons = {
            'waiting': 'bi-clock-history',
            'repairing': 'bi-tools',
            'completed': 'bi-check-circle'
        }
        return icons.get(self.status, '')
    
    def get_urgency_badge(self):
        """Mengembalikan class badge untuk urgensi"""
        badges = {
            'low': 'badge-low',
            'medium': 'badge-medium',
            'high': 'badge-high'
        }
        return badges.get(self.urgency, '')
    
    def get_urgency_icon(self):
        """Mengembalikan icon untuk urgensi"""
        icons = {
            'low': 'bi-arrow-down-circle',
            'medium': 'bi-exclamation-circle',
            'high': 'bi-exclamation-triangle'
        }
        return icons.get(self.urgency, '')
    
    def get_role_display(self):
        """Mendapatkan role pelapor"""
        return self.reporter.profile.get_role_display()
    
    def get_reporter_role(self):
        """Mendapatkan role pelapor untuk template"""
        return self.reporter.profile.role

class RepairHistory(models.Model):
    """
    Model untuk menyimpan riwayat perubahan status laporan
    """
    report = models.ForeignKey(FacilityReport, on_delete=models.CASCADE, related_name='history', verbose_name='Laporan')
    changed_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='repair_histories', verbose_name='Diubah Oleh')
    old_status = models.CharField('Status Sebelumnya', max_length=10, choices=FacilityReport.STATUS_CHOICES)
    new_status = models.CharField('Status Baru', max_length=10, choices=FacilityReport.STATUS_CHOICES)
    note = models.TextField('Catatan', blank=True, null=True, help_text='Catatan perubahan status')
    created_at = models.DateTimeField('Tanggal Perubahan', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Riwayat Perbaikan'
        verbose_name_plural = 'Riwayat Perbaikan'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.report.report_number} - {self.old_status} → {self.new_status}"
    
    def get_status_badge(self, status):
        """Mendapatkan badge untuk status tertentu"""
        badges = {
            'waiting': 'badge-waiting',
            'repairing': 'badge-repairing',
            'completed': 'badge-completed'
        }
        return badges.get(status, '')
    
    def get_status_display(self, status):
        """Mendapatkan display name untuk status"""
        status_map = dict(FacilityReport.STATUS_CHOICES)
        return status_map.get(status, status)
    
    def get_initial_icon(self):
        """Icon untuk timeline pertama (pembuatan laporan)"""
        return 'bi-plus-circle'