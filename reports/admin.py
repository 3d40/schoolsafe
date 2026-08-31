from django.contrib import admin
from .models import Location, DamageType, FacilityReport, RepairHistory

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    ordering = ('name',)

@admin.register(DamageType)
class DamageTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    ordering = ('name',)

@admin.register(FacilityReport)
class FacilityReportAdmin(admin.ModelAdmin):
    list_display = ('report_number', 'damage_type', 'location', 'urgency', 'status', 'priority_score', 'created_at')
    list_filter = ('status', 'urgency', 'location', 'damage_type', 'created_at')
    search_fields = ('report_number', 'description', 'reporter__username')
    readonly_fields = ('report_number', 'priority_score', 'created_at', 'updated_at', 'completed_at')
    ordering = ('-priority_score', '-created_at')
    
    fieldsets = (
        ('Informasi Laporan', {
            'fields': ('report_number', 'reporter', 'created_at')
        }),
        ('Detail Kerusakan', {
            'fields': ('damage_type', 'location', 'urgency', 'description', 'photo')
        }),
        ('Status dan Prioritas', {
            'fields': ('status', 'priority_score', 'admin_note')
        }),
        ('Tanggal', {
            'fields': ('updated_at', 'completed_at')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if change and 'status' in form.changed_data:
            # Catat perubahan status di history
            old_obj = FacilityReport.objects.get(pk=obj.pk)
            if old_obj.status != obj.status:
                RepairHistory.objects.create(
                    report=obj,
                    changed_by=request.user,
                    old_status=old_obj.status,
                    new_status=obj.status,
                    note=obj.admin_note
                )
        super().save_model(request, obj, form, change)

@admin.register(RepairHistory)
class RepairHistoryAdmin(admin.ModelAdmin):
    list_display = ('report', 'changed_by', 'old_status', 'new_status', 'created_at')
    list_filter = ('old_status', 'new_status', 'created_at')
    search_fields = ('report__report_number', 'note', 'changed_by__username')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)