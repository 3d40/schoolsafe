from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    # CRUD Laporan
    path('create/', views.create_report, name='create'),
    path('list/', views.report_list, name='list'),
    path('my/', views.my_reports, name='my_reports'),
    path('detail/<int:pk>/', views.report_detail, name='detail'),
    path('delete/<int:pk>/', views.delete_report, name='delete'),
]