from django import forms
from django.core.exceptions import ValidationError
from .models import FacilityReport, Location, DamageType

class ReportForm(forms.ModelForm):
    """
    Form untuk membuat laporan kerusakan
    """
    
    class Meta:
        model = FacilityReport
        fields = ['damage_type', 'location', 'urgency', 'description', 'photo']
        widgets = {
            'description': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Jelaskan kerusakan secara detail...',
                'class': 'form-control'
            }),
            'damage_type': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.Select(attrs={'class': 'form-select'}),
            'urgency': forms.Select(attrs={'class': 'form-select'}),
            'photo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'id': 'photo-input'
            }),
        }
        labels = {
            'damage_type': 'Jenis Kerusakan',
            'location': 'Lokasi Fasilitas',
            'urgency': 'Tingkat Urgensi',
            'description': 'Keterangan',
            'photo': 'Foto Kerusakan',
        }
        help_texts = {
            'description': 'Jelaskan kerusakan secara detail agar petugas dapat segera menanganinya.',
            'photo': 'Upload foto kerusakan (format: JPG, PNG, maksimal 5MB)',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Tambahkan class CSS untuk styling
        for field in self.fields:
            if field not in ['description', 'photo']:
                self.fields[field].widget.attrs.update({'class': 'form-select'})
        
        # Urutkan pilihan
        self.fields['damage_type'].queryset = DamageType.objects.filter(is_active=True).order_by('name')
        self.fields['location'].queryset = Location.objects.filter(is_active=True).order_by('name')
        
        # Tambahkan placeholder kosong
        self.fields['damage_type'].empty_label = 'Pilih Jenis Kerusakan'
        self.fields['location'].empty_label = 'Pilih Lokasi'
    
    def clean_photo(self):
        """Validasi foto yang diupload"""
        photo = self.cleaned_data.get('photo')
        
        if photo:
            # Cek ukuran file (maksimal 5MB)
            if photo.size > 5 * 1024 * 1024:
                raise ValidationError('Ukuran foto terlalu besar. Maksimal 5MB.')
            
            # Cek tipe file
            valid_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
            if photo.content_type not in valid_types:
                raise ValidationError('Format foto tidak didukung. Gunakan JPG, PNG, atau GIF.')
        
        return photo
    
    def clean(self):
        """Validasi tambahan"""
        cleaned_data = super().clean()
        
        # Pastikan deskripsi tidak terlalu pendek
        description = cleaned_data.get('description')
        if description and len(description) < 10:
            raise ValidationError('Keterangan terlalu pendek. Minimal 10 karakter.')
        
        return cleaned_data

class ReportUpdateStatusForm(forms.ModelForm):
    """
    Form untuk update status laporan (khusus admin)
    """
    
    class Meta:
        model = FacilityReport
        fields = ['status', 'admin_note']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'admin_note': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Catatan perbaikan...',
                'class': 'form-control'
            }),
        }
        labels = {
            'status': 'Status Laporan',
            'admin_note': 'Catatan Petugas',
        }
        help_texts = {
            'admin_note': 'Berikan catatan tentang perbaikan yang dilakukan.',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Tambahkan class CSS
        self.fields['status'].widget.attrs.update({'class': 'form-select'})
    
    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        admin_note = cleaned_data.get('admin_note')
        
        # Jika status selesai, wajib ada catatan
        if status == 'completed' and not admin_note:
            raise ValidationError('Catatan perbaikan wajib diisi ketika status Selesai.')
        
        return cleaned_data