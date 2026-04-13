from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import date

class Madrasah(models.Model):
    JENIS = [
        ('RA', 'Raudlatul Athfal (RA)'),
        ('MI', 'Madrasah Ibtidaiyah'),
        ('MTs', 'Madrasah Tsanawiyah'),
        ('MA', 'Madrasah Aliyah'),
    ]
    
    STATUS = [
        ('Negeri', 'Negeri'),
        ('Swasta', 'Swasta'),
    ]
    
    npsn = models.CharField('NPSN', max_length=8, unique=True)
    nama = models.CharField(max_length=200)
    jenis = models.CharField(max_length=3, choices=JENIS)
    status = models.CharField(max_length=7, choices=STATUS)
    alamat = models.TextField()
    desa = models.CharField(max_length=100)
    kecamatan = models.CharField(max_length=100)
    kabupaten = models.CharField(max_length=100)
    provinsi = models.CharField(max_length=100)
    kode_pos = models.CharField(max_length=5)
    telepon = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)
    kepala_madrasah = models.CharField(max_length=100)
    nip_kepala = models.CharField(max_length=18)
    akreditasi = models.CharField(max_length=1, choices=[
        ('A', 'A (Unggul)'), ('B', 'B (Baik)'), ('C', 'C (Cukup)')
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Madrasah'
    
    def __str__(self):
        return f"{self.nama} ({self.get_jenis_display()})"

class Guru(models.Model):
    JENJANG = [
        ('RA/PAUD', 'RA/PAUD'),
        ('SD/MI', 'SD/MI'),
        ('SMP/MTs', 'SMP/MTs'),
        ('SMA/MA', 'SMA/MA'),
    ]
    
    NUPTK = models.CharField(max_length=16, unique=True)
    nama = models.CharField(max_length=100)
    nip = models.CharField(max_length=18, blank=True)
    madrasah = models.ForeignKey(Madrasah, on_delete=models.CASCADE, related_name='gurus')
    jenis_kelamin = models.CharField(max_length=1, choices=[('L', 'Laki-laki'), ('P', 'Perempuan')])
    tempat_lahir = models.CharField(max_length=100)
    tanggal_lahir = models.DateField()
    pendidikan_terakhir = models.CharField(max_length=50)
    jurusan = models.CharField(max_length=100)
    tahun_lulus = models.IntegerField()
    status_kepegawaian = models.CharField(max_length=50, choices=[
        ('PNS', 'PNS'),
        ('PPPK', 'PPPK'),
        ('Honorer', 'Honorer'),
        ('GTY', 'GTY'),
    ])
    sertifikasi = models.BooleanField(default=False)
    bidang_studi = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.nama} - {self.madrasah.nama}"

class Supervisor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nip = models.CharField(max_length=18, unique=True)
    nama = models.CharField(max_length=100)
    pangkat = models.CharField(max_length=50)
    golongan = models.CharField(max_length=5)
    jabatan = models.CharField(max_length=100)
    wilayah_binaan = models.CharField(max_length=200)
    madrasah_binaan = models.ManyToManyField(Madrasah, related_name='supervisors')
    telepon = models.CharField(max_length=15)
    email = models.EmailField()
    
    def __str__(self):
        return f"{self.nama} - {self.wilayah_binaan}"

class InstrumenSupervisi(models.Model):
    KOMPONEN = [
        ('perencanaan', 'Perencanaan Pembelajaran'),
        ('pelaksanaan', 'Pelaksanaan Pembelajaran'),
        ('penilaian', 'Penilaian Pembelajaran'),
        ('tindak_lanjut', 'Tindak Lanjut'),
    ]
    
    kode = models.CharField(max_length=20, unique=True)
    komponen = models.CharField(max_length=20, choices=KOMPONEN)
    indikator = models.TextField()
    bobot = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(100)])
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Instrumen Supervisi'
    
    def __str__(self):
        return f"{self.kode} - {self.indikator[:50]}"

class HasilSupervisi(models.Model):
    supervisor = models.ForeignKey(Supervisor, on_delete=models.CASCADE)
    guru = models.ForeignKey(Guru, on_delete=models.CASCADE)
    madrasah = models.ForeignKey(Madrasah, on_delete=models.CASCADE)
    tanggal = models.DateField(default=date.today)
    semester = models.CharField(max_length=10, choices=[('Ganjil', 'Ganjil'), ('Genap', 'Genap')])
    tahun_ajaran = models.CharField(max_length=9)
    
    nilai_per_indikator = models.JSONField(default=dict)
    nilai_total = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    predikat = models.CharField(max_length=20, blank=True)
    
    rekomendasi = models.TextField()
    tindak_lanjut = models.TextField(blank=True)
    file_pendukung = models.FileField(upload_to='supervisi_files/', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if self.nilai_per_indikator:
            total = sum(self.nilai_per_indikator.values()) / len(self.nilai_per_indikator)
            self.nilai_total = round(total, 2)
            
            if total >= 91:
                self.predikat = 'A (Sangat Baik)'
            elif total >= 76:
                self.predikat = 'B (Baik)'
            elif total >= 61:
                self.predikat = 'C (Cukup)'
            else:
                self.predikat = 'D (Kurang)'
        
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name_plural = 'Hasil Supervisi'
        ordering = ['-tanggal']

# ============= INSTRUMEN SUPERVISI MANAJERIAL =============

class InstrumenManajerial(models.Model):
    KOMPONEN = [
        ('kurikulum', 'Pengelolaan Kurikulum'),
        ('ketenagaan', 'Pengelolaan Pendidik & Tenaga Kependidikan'),
        ('kesiswaan', 'Pengelolaan Kesiswaan'),
        ('sarana', 'Pengelolaan Sarana Prasarana'),
        ('pembiayaan', 'Pengelolaan Pembiayaan'),
        ('humas', 'Pengelolaan Hubungan Masyarakat'),
        ('layanan_khusus', 'Pengelolaan Layanan Khusus'),
        ('penjaminan_mutu', 'Sistem Penjaminan Mutu'),
    ]
    
    STANDAR_SNP = [
        ('isi', 'Standar Isi'),
        ('proses', 'Standar Proses'),
        ('lulusan', 'Standar Kompetensi Lulusan'),
        ('pendidik', 'Standar Pendidik & Tenaga Kependidikan'),
        ('sarana', 'Standar Sarana Prasarana'),
        ('pengelolaan', 'Standar Pengelolaan'),
        ('pembiayaan', 'Standar Pembiayaan'),
        ('penilaian', 'Standar Penilaian'),
    ]
    
    kode = models.CharField(max_length=20, unique=True)
    komponen = models.CharField(max_length=20, choices=KOMPONEN)
    standar_snp = models.CharField(max_length=20, choices=STANDAR_SNP, blank=True)
    indikator = models.TextField()
    bobot = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Instrumen Supervisi Manajerial'
    
    def __str__(self):
        return f"{self.kode} - {self.indikator[:50]}"


class HasilSupervisiManajerial(models.Model):
    supervisor = models.ForeignKey(Supervisor, on_delete=models.CASCADE)
    madrasah = models.ForeignKey(Madrasah, on_delete=models.CASCADE)
    tanggal = models.DateField(default=date.today)
    semester = models.CharField(max_length=10, choices=[('Ganjil', 'Ganjil'), ('Genap', 'Genap')])
    tahun_ajaran = models.CharField(max_length=9)
    
    nilai_per_indikator = models.JSONField(default=dict)
    nilai_total = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    predikat = models.CharField(max_length=20, blank=True)
    
    # Penilaian per komponen
    nilai_kurikulum = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    nilai_ketenagaan = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    nilai_kesiswaan = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    nilai_sarana = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    nilai_pembiayaan = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    nilai_humas = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    nilai_layanan_khusus = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    nilai_penjaminan_mutu = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    rekomendasi = models.TextField()
    tindak_lanjut = models.TextField(blank=True)
    file_pendukung = models.FileField(upload_to='supervisi_manajerial/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if self.nilai_per_indikator:
            total = sum(self.nilai_per_indikator.values()) / len(self.nilai_per_indikator)
            self.nilai_total = round(total, 2)
            
            if total >= 91:
                self.predikat = 'A (Sangat Baik)'
            elif total >= 76:
                self.predikat = 'B (Baik)'
            elif total >= 61:
                self.predikat = 'C (Cukup)'
            else:
                self.predikat = 'D (Kurang)'
        
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name_plural = 'Hasil Supervisi Manajerial'
        ordering = ['-tanggal']


# ============= PEMANTAUAN 8 STANDAR NASIONAL PENDIDIKAN =============

class PemantauanSNP(models.Model):
    STANDAR_CHOICES = [
        ('isi', 'Standar Isi'),
        ('proses', 'Standar Proses'),
        ('lulusan', 'Standar Kompetensi Lulusan'),
        ('pendidik', 'Standar Pendidik & Tenaga Kependidikan'),
        ('sarana', 'Standar Sarana Prasarana'),
        ('pengelolaan', 'Standar Pengelolaan'),
        ('pembiayaan', 'Standar Pembiayaan'),
        ('penilaian', 'Standar Penilaian'),
    ]
    
    STATUS = [
        ('belum', 'Belum Terpenuhi'),
        ('sebagian', 'Sebagian Terpenuhi'),
        ('terpenuhi', 'Terpenuhi'),
        ('unggul', 'Unggul'),
    ]
    
    madrasah = models.ForeignKey(Madrasah, on_delete=models.CASCADE, related_name='pemantauan_snp')
    standar = models.CharField(max_length=20, choices=STANDAR_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS, default='belum')
    skor = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    catatan = models.TextField(blank=True)
    rekomendasi = models.TextField(blank=True)
    tahun = models.IntegerField()
    semester = models.CharField(max_length=10, choices=[('Ganjil', 'Ganjil'), ('Genap', 'Genap')])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Pemantauan 8 SNP'
        unique_together = ['madrasah', 'standar', 'tahun', 'semester']
    
    def __str__(self):
        return f"{self.madrasah.nama} - {self.get_standar_display()} - {self.tahun}"


# ============= PROGRAM KEPENGAWASAN TAHUNAN =============

class ProgramKepengawasan(models.Model):
    supervisor = models.ForeignKey(Supervisor, on_delete=models.CASCADE)
    tahun = models.IntegerField()
    tujuan = models.TextField()
    target = models.TextField()
    jadwal = models.TextField()
    metode = models.TextField()
    indikator_keberhasilan = models.TextField()
    status = models.CharField(max_length=20, choices=[
        ('draft', 'Draft'),
        ('aktif', 'Aktif'),
        ('selesai', 'Selesai'),
        ('evaluasi', 'Evaluasi'),
    ], default='draft')
    file_program = models.FileField(upload_to='program_kepengawasan/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Program Kepengawasan'
    
    def __str__(self):
        return f"Program Kepengawasan {self.tahun} - {self.supervisor.nama}"

# ============= MODEL UNTUK REKAP KABUPATEN/KOTA =============

class Kecamatan(models.Model):
    nama = models.CharField(max_length=100)
    kabupaten = models.CharField(max_length=100, default='Kabupaten/Kota')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Kecamatan'
    
    def __str__(self):
        return f"{self.nama} - {self.kabupaten}"


class RekapBulanan(models.Model):
    periode = models.DateField()
    madrasah = models.ForeignKey('Madrasah', on_delete=models.CASCADE)
    rata_rata_akademik = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    rata_rata_manajerial = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    rata_rata_total = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    predikat = models.CharField(max_length=20, blank=True)
    jumlah_guru_disupervisi = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Rekap Bulanan'
        unique_together = ['periode', 'madrasah']
    
    def __str__(self):
        return f"{self.madrasah.nama} - {self.periode.strftime('%B %Y')}"

class TagihanPengawas(models.Model):
    STATUS = [
        ('pending', 'Pending'),
        ('dibayar', 'Dibayar'),
        ('overdue', 'Overdue'),
    ]
    
    madrasah = models.ForeignKey(Madrasah, on_delete=models.CASCADE)
    supervisor = models.ForeignKey(Supervisor, on_delete=models.CASCADE)
    nomor_tagihan = models.CharField(max_length=50, unique=True)
    tanggal = models.DateField(auto_now_add=True)
    jatuh_tempo = models.DateField()
    deskripsi = models.TextField()
    jumlah = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS, default='pending')
    file_tagihan = models.FileField(upload_to='tagihan/', blank=True)
    bukti_bayar = models.FileField(upload_to='bukti_bayar/', blank=True)
    catatan = models.TextField(blank=True)
    
    def __str__(self):
        return f"Tagihan {self.nomor_tagihan} - {self.madrasah.nama}"
    
# ============= INSTRUMEN SUPERVISI MANAJERIAL =============

class InstrumenManajerial(models.Model):
    KOMPONEN = [
        ('kurikulum', 'Pengelolaan Kurikulum'),
        ('ketenagaan', 'Pengelolaan Pendidik & Tenaga Kependidikan'),
        ('kesiswaan', 'Pengelolaan Kesiswaan'),
        ('sarana', 'Pengelolaan Sarana Prasarana'),
        ('pembiayaan', 'Pengelolaan Pembiayaan'),
        ('humas', 'Pengelolaan Hubungan Masyarakat'),
        ('layanan_khusus', 'Pengelolaan Layanan Khusus'),
        ('penjaminan_mutu', 'Sistem Penjaminan Mutu'),
    ]
    
    STANDAR_SNP = [
        ('isi', 'Standar Isi'),
        ('proses', 'Standar Proses'),
        ('lulusan', 'Standar Kompetensi Lulusan'),
        ('pendidik', 'Standar Pendidik & Tenaga Kependidikan'),
        ('sarana', 'Standar Sarana Prasarana'),
        ('pengelolaan', 'Standar Pengelolaan'),
        ('pembiayaan', 'Standar Pembiayaan'),
        ('penilaian', 'Standar Penilaian'),
    ]
    
    kode = models.CharField(max_length=20, unique=True)
    komponen = models.CharField(max_length=20, choices=KOMPONEN)
    standar_snp = models.CharField(max_length=20, choices=STANDAR_SNP, blank=True)
    indikator = models.TextField()
    bobot = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Instrumen Supervisi Manajerial'
    
    def __str__(self):
        return f"{self.kode} - {self.indikator[:50]}"


class HasilSupervisiManajerial(models.Model):
    supervisor = models.ForeignKey('Supervisor', on_delete=models.CASCADE)
    madrasah = models.ForeignKey('Madrasah', on_delete=models.CASCADE)
    tanggal = models.DateField(default=date.today)
    semester = models.CharField(max_length=10, choices=[('Ganjil', 'Ganjil'), ('Genap', 'Genap')])
    tahun_ajaran = models.CharField(max_length=9)
    
    nilai_per_indikator = models.JSONField(default=dict)
    nilai_total = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    predikat = models.CharField(max_length=20, blank=True)
    
    # Penilaian per komponen
    nilai_kurikulum = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    nilai_ketenagaan = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    nilai_kesiswaan = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    nilai_sarana = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    nilai_pembiayaan = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    nilai_humas = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    nilai_layanan_khusus = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    nilai_penjaminan_mutu = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    rekomendasi = models.TextField()
    tindak_lanjut = models.TextField(blank=True)
    file_pendukung = models.FileField(upload_to='supervisi_manajerial/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if self.nilai_per_indikator:
            total = sum(self.nilai_per_indikator.values()) / len(self.nilai_per_indikator)
            self.nilai_total = round(total, 2)
            
            if total >= 91:
                self.predikat = 'A (Sangat Baik)'
            elif total >= 76:
                self.predikat = 'B (Baik)'
            elif total >= 61:
                self.predikat = 'C (Cukup)'
            else:
                self.predikat = 'D (Kurang)'
        
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name_plural = 'Hasil Supervisi Manajerial'
        ordering = ['-tanggal']


class PemantauanSNP(models.Model):
    STANDAR_CHOICES = [
        ('isi', 'Standar Isi'),
        ('proses', 'Standar Proses'),
        ('lulusan', 'Standar Kompetensi Lulusan'),
        ('pendidik', 'Standar Pendidik & Tenaga Kependidikan'),
        ('sarana', 'Standar Sarana Prasarana'),
        ('pengelolaan', 'Standar Pengelolaan'),
        ('pembiayaan', 'Standar Pembiayaan'),
        ('penilaian', 'Standar Penilaian'),
    ]
    
    STATUS = [
        ('belum', 'Belum Terpenuhi'),
        ('sebagian', 'Sebagian Terpenuhi'),
        ('terpenuhi', 'Terpenuhi'),
        ('unggul', 'Unggul'),
    ]
    
    madrasah = models.ForeignKey('Madrasah', on_delete=models.CASCADE, related_name='pemantauan_snp')
    standar = models.CharField(max_length=20, choices=STANDAR_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS, default='belum')
    skor = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    catatan = models.TextField(blank=True)
    rekomendasi = models.TextField(blank=True)
    tahun = models.IntegerField()
    semester = models.CharField(max_length=10, choices=[('Ganjil', 'Ganjil'), ('Genap', 'Genap')])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Pemantauan 8 SNP'
        unique_together = ['madrasah', 'standar', 'tahun', 'semester']
    
    def __str__(self):
        return f"{self.madrasah.nama} - {self.get_standar_display()} - {self.tahun}"


class ProgramKepengawasan(models.Model):
    supervisor = models.ForeignKey('Supervisor', on_delete=models.CASCADE)
    tahun = models.IntegerField()
    tujuan = models.TextField()
    target = models.TextField()
    jadwal = models.TextField()
    metode = models.TextField()
    indikator_keberhasilan = models.TextField()
    status = models.CharField(max_length=20, choices=[
        ('draft', 'Draft'),
        ('aktif', 'Aktif'),
        ('selesai', 'Selesai'),
        ('evaluasi', 'Evaluasi'),
    ], default='draft')
    file_program = models.FileField(upload_to='program_kepengawasan/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
# ============= MODEL UNTUK REKAP KABUPATEN/KOTA =============

class Kecamatan(models.Model):
    nama = models.CharField(max_length=100)
    kabupaten = models.CharField(max_length=100, default='Kabupaten/Kota')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Kecamatan'
    
    def __str__(self):
        return f"{self.nama} - {self.kabupaten}"


class RekapBulanan(models.Model):
    periode = models.DateField()
    madrasah = models.ForeignKey('Madrasah', on_delete=models.CASCADE)
    rata_rata_akademik = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    rata_rata_manajerial = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    rata_rata_total = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    predikat = models.CharField(max_length=20, blank=True)
    jumlah_guru_disupervisi = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Rekap Bulanan'
        unique_together = ['periode', 'madrasah']
    
    def __str__(self):
        return f"{self.madrasah.nama} - {self.periode.strftime('%B %Y')}"

    class Meta:
        verbose_name_plural = 'Program Kepengawasan'
    
    def __str__(self):
        return f"Program Kepengawasan {self.tahun} - {self.supervisor.nama}"