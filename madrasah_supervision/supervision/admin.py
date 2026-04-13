from django.contrib import admin
from .models import Madrasah, Guru, Supervisor, InstrumenSupervisi, HasilSupervisi, TagihanPengawas

@admin.register(Madrasah)
class MadrasahAdmin(admin.ModelAdmin):
    list_display = ['npsn', 'nama', 'jenis', 'status', 'kepala_madrasah']
    search_fields = ['npsn', 'nama', 'kepala_madrasah']
    list_filter = ['jenis', 'status', 'akreditasi']
    list_per_page = 25

@admin.register(Guru)
class GuruAdmin(admin.ModelAdmin):
    list_display = ['NUPTK', 'nama', 'madrasah', 'bidang_studi']
    search_fields = ['NUPTK', 'nama', 'nip']
    list_filter = ['madrasah', 'jenis_kelamin', 'status_kepegawaian']
    list_per_page = 25

@admin.register(Supervisor)
class SupervisorAdmin(admin.ModelAdmin):
    list_display = ['nip', 'nama', 'wilayah_binaan']
    search_fields = ['nip', 'nama']
    filter_horizontal = ['madrasah_binaan']
    list_per_page = 25

@admin.register(InstrumenSupervisi)
class InstrumenSupervisiAdmin(admin.ModelAdmin):
    list_display = ['kode', 'komponen', 'indikator', 'bobot']
    list_filter = ['komponen']
    search_fields = ['kode', 'indikator']
    list_per_page = 25

@admin.register(HasilSupervisi)
class HasilSupervisiAdmin(admin.ModelAdmin):
    list_display = ['guru', 'madrasah', 'tanggal', 'nilai_total', 'predikat']
    list_filter = ['tanggal', 'semester', 'madrasah']
    search_fields = ['guru__nama', 'madrasah__nama']
    readonly_fields = ['nilai_total', 'predikat']
    list_per_page = 25

@admin.register(TagihanPengawas)
class TagihanPengawasAdmin(admin.ModelAdmin):
    list_display = ['nomor_tagihan', 'madrasah', 'tanggal', 'jatuh_tempo', 'jumlah', 'status']
    list_filter = ['status', 'tanggal']
    search_fields = ['nomor_tagihan', 'madrasah__nama']
    list_per_page = 25

from .models import InstrumenManajerial, HasilSupervisiManajerial, PemantauanSNP, ProgramKepengawasan

@admin.register(InstrumenManajerial)
class InstrumenManajerialAdmin(admin.ModelAdmin):
    list_display = ['kode', 'komponen', 'standar_snp', 'indikator', 'bobot']
    list_filter = ['komponen', 'standar_snp']
    search_fields = ['kode', 'indikator']

@admin.register(HasilSupervisiManajerial)
class HasilSupervisiManajerialAdmin(admin.ModelAdmin):
    list_display = ['madrasah', 'tanggal', 'semester', 'nilai_total', 'predikat']
    list_filter = ['tanggal', 'semester', 'madrasah']
    search_fields = ['madrasah__nama']
    readonly_fields = ['nilai_total', 'predikat']

@admin.register(PemantauanSNP)
class PemantauanSNPAdmin(admin.ModelAdmin):
    list_display = ['madrasah', 'standar', 'status', 'skor', 'tahun', 'semester']
    list_filter = ['standar', 'status', 'tahun', 'semester']
    search_fields = ['madrasah__nama']

@admin.register(ProgramKepengawasan)
class ProgramKepengawasanAdmin(admin.ModelAdmin):
    list_display = ['supervisor', 'tahun', 'status', 'created_at']
    list_filter = ['tahun', 'status']
    search_fields = ['supervisor__nama']

from .models import Kecamatan, RekapBulanan

@admin.register(Kecamatan)
class KecamatanAdmin(admin.ModelAdmin):
    list_display = ['nama', 'kabupaten']
    search_fields = ['nama', 'kabupaten']

@admin.register(RekapBulanan)
class RekapBulananAdmin(admin.ModelAdmin):
    list_display = ['madrasah', 'periode', 'rata_rata_total', 'predikat']
    list_filter = ['periode', 'predikat']
    search_fields = ['madrasah__nama']