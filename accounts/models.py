from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    """
    Model profil pengguna untuk menambahkan role ke User Django
    """
    ROLE_CHOICES = (
        ('siswa', 'Siswa'),
        ('guru', 'Guru'),
        ('admin', 'Admin'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField('Peran', max_length=10, choices=ROLE_CHOICES, default='siswa')
    phone = models.CharField('Nomor Telepon', max_length=15, blank=True, null=True)
    class_name = models.CharField('Kelas', max_length=10, blank=True, null=True)  # Untuk siswa
    created_at = models.DateTimeField('Tanggal Dibuat', auto_now_add=True)
    updated_at = models.DateTimeField('Tanggal Diperbarui', auto_now=True)
    
    class Meta:
        verbose_name = 'Profil'
        verbose_name_plural = 'Profil Pengguna'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"
    
    def is_student(self):
        return self.role == 'siswa'
    
    def is_teacher(self):
        return self.role == 'guru'
    
    def is_admin(self):
        return self.role == 'admin'

# Signal untuk membuat Profile otomatis ketika User dibuat
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()