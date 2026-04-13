from django.urls import path
from . import views

app_name = 'supervision'

urlpatterns = [
    # Dashboard & Utama
    path('', views.dashboard, name='dashboard'),
    
    # Supervisi Akademik
    path('input-supervisi/', views.input_supervisi, name='input_supervisi'),
    path('riwayat-supervisi/', views.riwayat_supervisi, name='riwayat_supervisi'),
    path('detail-supervisi/<int:pk>/', views.detail_supervisi, name='detail_supervisi'),
    
    # Data Binaan
    path('madrasah-binaan/', views.daftar_madrasah_binaan, name='daftar_madrasah_binaan'),
    path('guru-binaan/', views.daftar_guru_binaan, name='daftar_guru_binaan'),
    path('guru-binaan/<int:madrasah_id>/', views.daftar_guru_binaan, name='daftar_guru_binaan_by_madrasah'),
    path('get-guru-by-madrasah/', views.get_guru_by_madrasah, name='get_guru_by_madrasah'),
    
    # Laporan PDF
    path('laporan-pdf/<int:madrasah_id>/', views.generate_laporan_pdf, name='laporan_pdf'),
    path('laporan-pdf/<int:madrasah_id>/<int:guru_id>/', views.generate_laporan_pdf, name='laporan_pdf_guru'),
    
    # Import Export
    path('import-data/', views.import_data, name='import_data'),
    path('export-data/<str:model_name>/', views.export_data, name='export_data'),
    
    # Tagihan
    path('kelola-tagihan/', views.kelola_tagihan, name='kelola_tagihan'),
    
    # Supervisi Manajerial
    path('input-supervisi-manajerial/', views.input_supervisi_manajerial, name='input_supervisi_manajerial'),
    path('riwayat-supervisi-manajerial/', views.riwayat_supervisi_manajerial, name='riwayat_supervisi_manajerial'),
    
    # 8 SNP
    path('dashboard-snp/', views.dashboard_snp, name='dashboard_snp'),
    
    # Rekap Kabupaten
    path('dashboard-rekap-kabupaten/', views.dashboard_rekap_kabupaten, name='dashboard_rekap_kabupaten'),
    path('export-lengkap-excel/', views.export_lengkap_excel, name='export_lengkap_excel'),
    path('kirim-notifikasi-email/', views.kirim_notifikasi_email, name='kirim_notifikasi_email'),
    
    # Laporan Periode
    path('laporan-periode/', views.laporan_periode, name='laporan_periode'),
    path('export-laporan/<str:jenis>/<int:tahun>/', views.export_laporan_pdf, name='export_laporan'),
    path('export-laporan/<str:jenis>/<int:tahun>/<int:periode>/', views.export_laporan_pdf, name='export_laporan_periode'),
    path('export-laporan-tahunan/<int:tahun>/', views.export_laporan_tahunan, name='export_laporan_tahunan'),
    
    # Kepala Madrasah
    path('hasil-supervisi-kepsek/', views.hasil_supervisi_kepsek, name='hasil_supervisi_kepsek'),
    path('detail-supervisi-kepsek/<int:pk>/<str:jenis>/', views.detail_supervisi_kepsek, name='detail_supervisi_kepsek'),
    path('detail-supervisi-manajerial/<int:pk>/', views.detail_supervisi_manajerial, name='detail_supervisi_manajerial'),
    path('laporan-manajerial-pdf/<int:pk>/', views.laporan_manajerial_pdf, name='laporan_manajerial_pdf'),
]