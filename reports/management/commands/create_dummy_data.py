from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from accounts.models import Profile
from reports.models import Location, DamageType, FacilityReport, RepairHistory
import random
from datetime import timedelta

class Command(BaseCommand):
    help = 'Membuat data dummy untuk SchoolSafe'
    
    def handle(self, *args, **options):
        self.stdout.write('Membuat data dummy SchoolSafe...')
        
        # 1. Buat lokasi
        locations_data = [
            {'name': 'Kelas 7A', 'description': 'Ruang kelas 7A'},
            {'name': 'Kelas 7B', 'description': 'Ruang kelas 7B'},
            {'name': 'Kelas 7C', 'description': 'Ruang kelas 7C'},
            {'name': 'Kelas 8A', 'description': 'Ruang kelas 8A'},
            {'name': 'Kelas 8B', 'description': 'Ruang kelas 8B'},
            {'name': 'Kelas 8C', 'description': 'Ruang kelas 8C'},
            {'name': 'Kelas 9A', 'description': 'Ruang kelas 9A'},
            {'name': 'Kelas 9B', 'description': 'Ruang kelas 9B'},
            {'name': 'Kelas 9C', 'description': 'Ruang kelas 9C'},
            {'name': 'Laboratorium IPA', 'description': 'Laboratorium IPA'},
            {'name': 'Laboratorium Komputer', 'description': 'Laboratorium Komputer'},
            {'name': 'Perpustakaan', 'description': 'Perpustakaan sekolah'},
            {'name': 'Toilet Lantai 1', 'description': 'Toilet lantai 1'},
            {'name': 'Toilet Lantai 2', 'description': 'Toilet lantai 2'},
            {'name': 'Kantin', 'description': 'Kantin sekolah'},
            {'name': 'Lapangan', 'description': 'Lapangan sekolah'},
            {'name': 'Ruang Guru', 'description': 'Ruang guru'},
            {'name': 'Ruang Kepala Sekolah', 'description': 'Ruang kepala sekolah'},
            {'name': 'Aula', 'description': 'Aula sekolah'},
            {'name': 'Musholla', 'description': 'Musholla sekolah'},
        ]
        
        locations = []
        for loc_data in locations_data:
            location, created = Location.objects.get_or_create(
                name=loc_data['name'],
                defaults={'description': loc_data['description']}
            )
            locations.append(location)
            if created:
                self.stdout.write(f'  Lokasi dibuat: {location.name}')
        
        # 2. Buat jenis kerusakan
        damage_types_data = [
            {'name': 'Lampu Mati', 'description': 'Lampu tidak menyala atau rusak'},
            {'name': 'Keran Bocor', 'description': 'Keran air bocor atau tidak bisa ditutup'},
            {'name': 'Kursi Rusak', 'description': 'Kursi patah atau tidak nyaman'},
            {'name': 'Meja Rusak', 'description': 'Meja rusak atau goyang'},
            {'name': 'Kabel Listrik Terbuka', 'description': 'Kabel listrik terbuka dan berbahaya'},
            {'name': 'AC Tidak Dingin', 'description': 'AC tidak berfungsi dengan baik'},
            {'name': 'Proyektor Rusak', 'description': 'Proyektor tidak bisa menyala'},
            {'name': 'Papan Tulis Rusak', 'description': 'Papan tulis rusak atau tidak bisa dipakai'},
            {'name': 'Jendela Pecah', 'description': 'Jendela kaca pecah atau retak'},
            {'name': 'Pintu Rusak', 'description': 'Pintu tidak bisa dibuka/ditutup'},
            {'name': 'Kipas Angin Rusak', 'description': 'Kipas angin tidak berfungsi'},
            {'name': 'Toilet Mampet', 'description': 'Toilet tersumbat atau tidak bisa disiram'},
            {'name': 'Wastafel Rusak', 'description': 'Wastafel rusak atau bocor'},
            {'name': 'Atap Bocor', 'description': 'Atap bocor saat hujan'},
            {'name': 'Keramik Lepas', 'description': 'Keramik lantai lepas atau retak'},
        ]
        
        damage_types = []
        for dt_data in damage_types_data:
            damage_type, created = DamageType.objects.get_or_create(
                name=dt_data['name'],
                defaults={'description': dt_data['description']}
            )
            damage_types.append(damage_type)
            if created:
                self.stdout.write(f'  Jenis kerusakan dibuat: {damage_type.name}')
        
        # 3. Buat user
        users_data = [
            {'username': 'siswa1', 'password': 'siswa123', 'role': 'siswa', 'first_name': 'Ahmad', 'last_name': 'Fauzi', 'class_name': '7A'},
            {'username': 'siswa2', 'password': 'siswa123', 'role': 'siswa', 'first_name': 'Siti', 'last_name': 'Nurhaliza', 'class_name': '7B'},
            {'username': 'siswa3', 'password': 'siswa123', 'role': 'siswa', 'first_name': 'Budi', 'last_name': 'Santoso', 'class_name': '8A'},
            {'username': 'siswa4', 'password': 'siswa123', 'role': 'siswa', 'first_name': 'Dewi', 'last_name': 'Lestari', 'class_name': '8B'},
            {'username': 'siswa5', 'password': 'siswa123', 'role': 'siswa', 'first_name': 'Eko', 'last_name': 'Prasetyo', 'class_name': '9A'},
            {'username': 'guru1', 'password': 'guru123', 'role': 'guru', 'first_name': 'Ibu', 'last_name': 'Siti', 'class_name': None},
            {'username': 'guru2', 'password': 'guru123', 'role': 'guru', 'first_name': 'Bapak', 'last_name': 'Joko', 'class_name': None},
            {'username': 'admin', 'password': 'admin123', 'role': 'admin', 'first_name': 'Petugas', 'last_name': 'Sarana', 'class_name': None},
        ]
        
        users = []
        for user_data in users_data:
            # Cek apakah user sudah ada
            if User.objects.filter(username=user_data['username']).exists():
                user = User.objects.get(username=user_data['username'])
                self.stdout.write(f'  User sudah ada: {user.username}')
            else:
                user = User.objects.create_user(
                    username=user_data['username'],
                    password=user_data['password'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name']
                )
                # Update profile
                profile = user.profile
                profile.role = user_data['role']
                if user_data['class_name']:
                    profile.class_name = user_data['class_name']
                profile.save()
                self.stdout.write(f'  User dibuat: {user.username} - {user_data["role"]}')
            users.append(user)
        
        # 4. Buat laporan dummy
        statuses = ['waiting', 'repairing', 'completed']
        urgencies = ['low', 'medium', 'high']
        
        # Sample laporan
        sample_reports = [
            {'damage': 'Lampu Mati', 'desc': 'Lampu di ruang kelas mati sehingga ruangan menjadi gelap', 'note': 'Ganti lampu baru'},
            {'damage': 'Keran Bocor', 'desc': 'Keran air di toilet terus mengalir meskipun sudah ditutup rapat', 'note': 'Perbaiki keran atau ganti seal'},
            {'damage': 'Kursi Rusak', 'desc': 'Kursi di kelas goyang dan tidak stabil, berbahaya untuk digunakan', 'note': 'Las kaki kursi atau ganti yang baru'},
            {'damage': 'Meja Rusak', 'desc': 'Meja belajar di kelas bagian kakinya patah', 'note': 'Perbaiki kaki meja'},
            {'damage': 'Kabel Listrik Terbuka', 'desc': 'Ada kabel listrik terbuka di laboratorium, sangat berbahaya', 'note': 'Segera tutup dan perbaiki kabel'},
            {'damage': 'AC Tidak Dingin', 'desc': 'AC di ruang guru tidak mengeluarkan udara dingin', 'note': 'Cek freon dan kebersihan AC'},
            {'damage': 'Proyektor Rusak', 'desc': 'Proyektor di kelas tidak bisa menampilkan gambar', 'note': 'Cek lampu proyektor'},
            {'damage': 'Papan Tulis Rusak', 'desc': 'Papan tulis sudah sulit dibersihkan dan banyak coretan', 'note': 'Cat ulang papan tulis'},
            {'damage': 'Jendela Pecah', 'desc': 'Jendela kelas pecah terkena bola', 'note': 'Ganti kaca jendela'},
            {'damage': 'Pintu Rusak', 'desc': 'Pintu kelas tidak bisa ditutup dengan baik', 'note': 'Perbaiki engsel pintu'},
            {'damage': 'Toilet Mampet', 'desc': 'Toilet di lantai 2 mampet dan tidak bisa disiram', 'note': 'Sedot WC dan perbaiki saluran'},
            {'damage': 'Atap Bocor', 'desc': 'Atap kelas bocor saat hujan, air menetes ke meja belajar', 'note': 'Perbaiki atap yang bocor'},
        ]
        
        # Pilih beberapa laporan yang akan dibuat
        num_reports = 20
        for i in range(num_reports):
            # Pilih data acak
            sample = random.choice(sample_reports)
            damage_type = DamageType.objects.get(name=sample['damage'])
            location = random.choice(locations)
            urgency = random.choice(urgencies)
            status = random.choice(statuses)
            reporter = random.choice(users)
            
            # Buat tanggal acak dalam 30 hari terakhir
            days_ago = random.randint(0, 30)
            hours_ago = random.randint(0, 23)
            created_date = timezone.now() - timedelta(days=days_ago, hours=hours_ago)
            
            # Buat laporan
            report = FacilityReport.objects.create(
                reporter=reporter,
                damage_type=damage_type,
                location=location,
                urgency=urgency,
                description=sample['desc'],
                status=status,
                admin_note=sample['note'] if status != 'waiting' else None,
                created_at=created_date,
                updated_at=created_date,
            )
            
            # Set completed_at jika status selesai
            if status == 'completed':
                completed_date = created_date + timedelta(hours=random.randint(1, 48))
                report.completed_at = completed_date
                report.save()
            
            # Buat riwayat perbaikan
            # History 1: Pembuatan laporan
            RepairHistory.objects.create(
                report=report,
                changed_by=reporter,
                old_status='waiting',
                new_status='waiting',
                note=f'Laporan dibuat oleh {reporter.get_full_name()}',
                created_at=created_date
            )
            
            # History 2: Jika status repairing
            if status in ['repairing', 'completed']:
                repairing_date = created_date + timedelta(hours=random.randint(1, 12))
                repairer = User.objects.get(username='admin')
                RepairHistory.objects.create(
                    report=report,
                    changed_by=repairer,
                    old_status='waiting',
                    new_status='repairing',
                    note='Petugas mulai menangani laporan',
                    created_at=repairing_date
                )
                
                # Update report dengan tanggal repairing
                report.updated_at = repairing_date
                report.save()
            
            # History 3: Jika status completed
            if status == 'completed':
                completed_date = report.completed_at or (created_date + timedelta(hours=random.randint(12, 48)))
                repairer = User.objects.get(username='admin')
                RepairHistory.objects.create(
                    report=report,
                    changed_by=repairer,
                    old_status='repairing',
                    new_status='completed',
                    note=sample['note'],
                    created_at=completed_date
                )
                
                # Update report
                report.completed_at = completed_date
                report.updated_at = completed_date
                report.save()
            
            self.stdout.write(f'  Laporan dibuat: {report.report_number} - {report.damage_type.name}')
        
        self.stdout.write(self.style.SUCCESS('✅ Data dummy berhasil dibuat!'))
        self.stdout.write(f'  - {len(locations)} lokasi')
        self.stdout.write(f'  - {len(damage_types)} jenis kerusakan')
        self.stdout.write(f'  - {len(users)} pengguna')
        self.stdout.write(f'  - {num_reports} laporan')