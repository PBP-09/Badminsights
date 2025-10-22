from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from badminews.models import News
from datetime import timedelta
from django.utils import timezone

class Command(BaseCommand):
    help = 'Populate database with dummy news data'

    def handle(self, *args, **options):
        # Create a dummy user if it doesn't exist
        user, created = User.objects.get_or_create(
            username='admin',
            defaults={'email': 'admin@example.com'}
        )
        if created:
            user.set_password('password')
            user.save()

        # Dummy news data
        news_data = [
            {
                'title': 'Indonesia Raih Medali Emas di Kejuaraan Dunia Bulu Tangkis 2025',
                'content': 'Tim bulu tangkis Indonesia berhasil meraih medali emas di Kejuaraan Dunia Bulu Tangkis 2025 yang diselenggarakan di Paris, Prancis. Pasangan ganda campuran Indonesia, Kevin Sanjaya Sukamuljo dan Greysia Polii, tampil dominan sepanjang turnamen dan berhasil mengalahkan pasangan China di final. Ini adalah medali emas ke-15 Indonesia di ajang Kejuaraan Dunia.',
                'category': 'tournament',
            },
            {
                'title': 'Pemain Muda Indonesia Siap Bersaing di Olimpiade 2028',
                'content': 'Federasi Bulu Tangkis Dunia (BWF) telah mengumumkan daftar pemain muda potensial yang akan menjadi bintang masa depan bulu tangkis dunia. Dari Indonesia, nama-nama seperti Chico Aura Dwi Wardoyo dan Ester Nurumi Tri Wardoyo masuk dalam daftar tersebut. Keduanya telah menunjukkan performa impresif di berbagai turnamen junior internasional.',
                'category': 'player',
            },
            {
                'title': 'Teknologi Baru dalam Raket Bulu Tangkis Era Digital',
                'content': 'Produsen raket bulu tangkis terkemuka meluncurkan teknologi baru yang menggabungkan kecerdasan buatan untuk mengoptimalkan performa pemain. Teknologi ini dapat menganalisis gaya pukulan pemain dan memberikan rekomendasi penyesuaian raket secara real-time. Inovasi ini diharapkan dapat meningkatkan akurasi dan kekuatan pukulan pemain profesional.',
                'category': 'general',
            },
            {
                'title': 'Turnamen All England 2026: Jadwal dan Peserta Terbaru',
                'content': 'Panitia penyelenggara All England Open 2026 telah merilis jadwal lengkap dan daftar peserta awal. Turnamen bergengsi ini akan digelar di Birmingham, Inggris, pada bulan Maret 2026. Banyak pemain top dunia telah mengkonfirmasi keikutsertaan mereka, termasuk pemain Indonesia seperti Anthony Sinisuka Ginting dan Jonatan Christie.',
                'category': 'tournament',
            },
            {
                'title': 'Sejarah Bulu Tangkis: Dari Olahraga Tradisional ke Olahraga Global',
                'content': 'Bulu tangkis telah berkembang dari olahraga tradisional di Asia menjadi olahraga global yang dipertandingkan di Olimpiade. Artikel ini mengulas perjalanan panjang bulu tangkis dari permainan di halaman rumah menjadi cabang olahraga yang menghasilkan jutaan dolar dalam industri olahraga dunia.',
                'category': 'general',
            },
            {
                'title': 'Strategi Pelatihan Atlet Bulu Tangkis Masa Kini',
                'content': 'Pelatih bulu tangkis modern menggunakan kombinasi teknologi canggih dan metode pelatihan tradisional untuk mengembangkan atlet. Dari analisis video high-speed hingga program latihan berbasis data, para pelatih terus berinovasi untuk menciptakan generasi atlet bulu tangkis yang lebih tangguh dan kompetitif.',
                'category': 'general',
            },
            {
                'title': 'Profil: Anthony Sinisuka Ginting, Bintang Bulu Tangkis Indonesia',
                'content': 'Anthony Sinisuka Ginting telah menjadi salah satu pemain tunggal putra terbaik dunia. Dengan gaya permainan agresif dan kemampuan smash yang mematikan, Ginting telah memenangkan berbagai gelar internasional. Artikel ini mengulas perjalanan karier Ginting dari pemain junior hingga menjadi pemain top dunia.',
                'category': 'player',
            },
            {
                'title': 'Persiapan Indonesia Menghadapi Piala Sudirman 2026',
                'content': 'Tim bulu tangkis Indonesia sedang intensif mempersiapkan diri untuk Piala Sudirman 2026. Pelatih kepala, Herry Iman Pierngadi, telah merancang program latihan khusus yang fokus pada kekompakan tim dan strategi permainan. Piala Sudirman merupakan ajang bergengsi yang mempertemukan tim nasional dari seluruh dunia.',
                'category': 'tournament',
            },
        ]

        # Create news entries
        for i, data in enumerate(news_data):
            news, created = News.objects.get_or_create(
                title=data['title'],
                defaults={
                    'content': data['content'],
                    'author': user,
                    'category': data['category'],
                    'date_published': timezone.now() - timedelta(days=i*2),  # Spread over time
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created news: {news.title}'))
            else:
                self.stdout.write(f'News already exists: {news.title}')

        self.stdout.write(self.style.SUCCESS('Successfully populated news data'))