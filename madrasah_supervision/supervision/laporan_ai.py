"""
MODUL AI UNTUK GENERATE LAPORAN PROFESIONAL
Menggunakan OpenAI API (atau Hugging Face sebagai alternatif gratis)
"""

import json
from datetime import datetime
from django.db.models import Avg, Count, Sum, Q
from .models import Madrasah, Guru, HasilSupervisi, HasilSupervisiManajerial, Kecamatan

# ============= KONFIGURASI AI =============
# Pilih salah satu:

# OPSI 1: OpenAI API (Berbayar, lebih bagus)
# OPENAI_API_KEY = "sk-xxxxx"  # Ganti dengan API key Anda

# OPSI 2: Hugging Face (Gratis, perlu registrasi)
# HUGGINGFACE_API_KEY = "hf_xxxxx"

# OPSI 3: Template-based (Tanpa API, tetap profesional)
USE_AI = False  # Set True jika punya API key


def get_statistik_periode(tahun, bulan=None, triwulan=None, semester=None):
    """Ambil data statistik berdasarkan periode"""
    
    # Filter berdasarkan periode
    if bulan:
        tanggal_start = datetime(tahun, bulan, 1)
        if bulan == 12:
            tanggal_end = datetime(tahun+1, 1, 1)
        else:
            tanggal_end = datetime(tahun, bulan+1, 1)
    elif triwulan:
        if triwulan == 1:
            tanggal_start = datetime(tahun, 1, 1)
            tanggal_end = datetime(tahun, 4, 1)
        elif triwulan == 2:
            tanggal_start = datetime(tahun, 4, 1)
            tanggal_end = datetime(tahun, 7, 1)
        elif triwulan == 3:
            tanggal_start = datetime(tahun, 7, 1)
            tanggal_end = datetime(tahun, 10, 1)
        else:
            tanggal_start = datetime(tahun, 10, 1)
            tanggal_end = datetime(tahun+1, 1, 1)
    elif semester:
        if semester == 1:
            tanggal_start = datetime(tahun, 1, 1)
            tanggal_end = datetime(tahun, 7, 1)
        else:
            tanggal_start = datetime(tahun, 7, 1)
            tanggal_end = datetime(tahun+1, 1, 1)
    else:  # tahunan
        tanggal_start = datetime(tahun, 1, 1)
        tanggal_end = datetime(tahun+1, 1, 1)
    
    # Ambil data supervisi dalam periode
    supervisi_akademik = HasilSupervisi.objects.filter(
        tanggal__gte=tanggal_start,
        tanggal__lt=tanggal_end
    )
    
    supervisi_manajerial = HasilSupervisiManajerial.objects.filter(
        tanggal__gte=tanggal_start,
        tanggal__lt=tanggal_end
    )
    
    # Statistik
    total_madrasah = Madrasah.objects.count()
    total_guru = Guru.objects.count()
    total_supervisi_akademik = supervisi_akademik.count()
    total_supervisi_manajerial = supervisi_manajerial.count()
    rata_akademik = supervisi_akademik.aggregate(avg=Avg('nilai_total'))['avg'] or 0
    rata_manajerial = supervisi_manajerial.aggregate(avg=Avg('nilai_total'))['avg'] or 0
    
    # Distribusi predikat
    predikat_akademik = {
        'A': supervisi_akademik.filter(nilai_total__gte=91).count(),
        'B': supervisi_akademik.filter(nilai_total__gte=76, nilai_total__lt=91).count(),
        'C': supervisi_akademik.filter(nilai_total__gte=61, nilai_total__lt=76).count(),
        'D': supervisi_akademik.filter(nilai_total__lt=61).count(),
    }
    
    # Rekap per kecamatan
    rekap_kecamatan = []
    for kec in Kecamatan.objects.all():
        madrasah_kec = Madrasah.objects.filter(kecamatan=kec.nama)
        nilai_kec = supervisi_akademik.filter(madrasah__in=madrasah_kec).aggregate(avg=Avg('nilai_total'))['avg'] or 0
        rekap_kecamatan.append({
            'nama': kec.nama,
            'nilai': round(nilai_kec, 2),
            'jml_madrasah': madrasah_kec.count()
        })
    
    return {
        'total_madrasah': total_madrasah,
        'total_guru': total_guru,
        'total_supervisi_akademik': total_supervisi_akademik,
        'total_supervisi_manajerial': total_supervisi_manajerial,
        'rata_akademik': round(rata_akademik, 2),
        'rata_manajerial': round(rata_manajerial, 2),
        'predikat_akademik': predikat_akademik,
        'rekap_kecamatan': rekap_kecamatan,
        'tanggal_start': tanggal_start,
        'tanggal_end': tanggal_end,
    }


def generate_laporan_ai(statistik, periode_nama, tahun):
    """Generate laporan menggunakan AI atau template"""
    
    if USE_AI and 'OPENAI_API_KEY' in globals():
        return generate_laporan_openai(statistik, periode_nama, tahun)
    else:
        return generate_laporan_template(statistik, periode_nama, tahun)


def generate_laporan_openai(statistik, periode_nama, tahun):
    """Generate laporan menggunakan OpenAI API"""
    
    try:
        import openai
        openai.api_key = OPENAI_API_KEY
        
        prompt = f"""
        Buatkan laporan pengawasan madrasah yang profesional dengan data berikut:
        
        Periode: {periode_nama} {tahun}
        Total Madrasah: {statistik['total_madrasah']}
        Total Guru: {statistik['total_guru']}
        Total Supervisi Akademik: {statistik['total_supervisi_akademik']}
        Total Supervisi Manajerial: {statistik['total_supervisi_manajerial']}
        Rata-rata Nilai Akademik: {statistik['rata_akademik']}
        Rata-rata Nilai Manajerial: {statistik['rata_manajerial']}
        
        Distribusi Predikat:
        - A (Sangat Baik): {statistik['predikat_akademik']['A']} supervisi
        - B (Baik): {statistik['predikat_akademik']['B']} supervisi
        - C (Cukup): {statistik['predikat_akademik']['C']} supervisi
        - D (Kurang): {statistik['predikat_akademik']['D']} supervisi
        
        Format laporan:
        1. Ringkasan Eksekutif
        2. Analisis Data
        3. Temuan Utama
        4. Rekomendasi
        5. Kesimpulan
        
        Gunakan bahasa Indonesia formal dan profesional.
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1500
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"AI Error: {e}")
        return generate_laporan_template(statistik, periode_nama, tahun)


def generate_laporan_template(statistik, periode_nama, tahun):
    """Generate laporan menggunakan template profesional (tanpa AI)"""
    
    # Hitung persentase
    total_supervisi = statistik['total_supervisi_akademik']
    persen_a = (statistik['predikat_akademik']['A'] / total_supervisi * 100) if total_supervisi > 0 else 0
    persen_b = (statistik['predikat_akademik']['B'] / total_supervisi * 100) if total_supervisi > 0 else 0
    persen_c = (statistik['predikat_akademik']['C'] / total_supervisi * 100) if total_supervisi > 0 else 0
    persen_d = (statistik['predikat_akademik']['D'] / total_supervisi * 100) if total_supervisi > 0 else 0
    
    # Tentukan kualitas berdasarkan nilai rata-rata
    rata_total = (statistik['rata_akademik'] + statistik['rata_manajerial']) / 2
    if rata_total >= 91:
        kualitas = "SANGAT BAIK (A)"
        warna = "hijau"
    elif rata_total >= 76:
        kualitas = "BAIK (B)"
        warna = "biru"
    elif rata_total >= 61:
        kualitas = "CUKUP (C)"
        warna = "kuning"
    else:
        kualitas = "KURANG (D)"
        warna = "merah"
    
    # Buat tabel rekap kecamatan
    tabel_kecamatan = ""
    for kec in statistik['rekap_kecamatan']:
        tabel_kecamatan += f"""
        <tr>
            <td>{kec['nama']}</td>
            <td>{kec['jml_madrasah']}</td>
            <td>{kec['nilai']}</td>
            <td>{'🟢' if kec['nilai'] >= 76 else '🟡' if kec['nilai'] >= 61 else '🔴'}</td>
        </tr>
        """
    
    laporan = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Laporan Pengawasan Madrasah - {periode_nama} {tahun}</title>
    <style>
        @page {{
            size: A4;
            margin: 2.5cm;
        }}
        body {{
            font-family: 'Times New Roman', 'Calibri', sans-serif;
            line-height: 1.5;
            color: #333;
            font-size: 12pt;
        }}
        h1 {{
            text-align: center;
            font-size: 18pt;
            margin-bottom: 5px;
            color: #2c3e50;
        }}
        h2 {{
            font-size: 14pt;
            margin-top: 20px;
            margin-bottom: 10px;
            color: #34495e;
            border-bottom: 2px solid #3498db;
            padding-bottom: 5px;
        }}
        h3 {{
            font-size: 12pt;
            margin-top: 15px;
            margin-bottom: 8px;
            color: #2c3e50;
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        .subtitle {{
            text-align: center;
            font-size: 10pt;
            color: #666;
        }}
        .ringkasan {{
            background: #f8f9fa;
            padding: 15px;
            border-left: 4px solid #3498db;
            margin: 20px 0;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}
        th {{
            background-color: #3498db;
            color: white;
        }}
        .kualitas-unggul {{ color: #27ae60; }}
        .kualitas-baik {{ color: #2980b9; }}
        .kualitas-cukup {{ color: #f39c12; }}
        .kualitas-kurang {{ color: #e74c3c; }}
        .footer {{
            text-align: center;
            margin-top: 50px;
            font-size: 10pt;
            border-top: 1px solid #ddd;
            padding-top: 20px;
        }}
        .signature {{
            margin-top: 40px;
            text-align: right;
        }}
    </style>
</head>
<body>

<div class="header">
    <h1>LAPORAN PENGAWASAN MADRASAH</h1>
    <h2>Periode {periode_nama} {tahun}</h2>
    <div class="subtitle">
        Dinas Pendidikan Kabupaten/Kota<br>
        Berdasarkan Regulasi Kemenag RI No. 15 Tahun 2024
    </div>
</div>

<!-- RINGKASAN EKSEKUTIF -->
<h2>I. RINGKASAN EKSEKUTIF</h2>
<div class="ringkasan">
    <p>Selama periode <strong>{periode_nama} {tahun}</strong>, telah dilaksanakan pengawasan terhadap 
    <strong>{statistik['total_madrasah']} madrasah</strong> dengan total <strong>{statistik['total_guru']} guru</strong> 
    yang tersebar di Kabupaten/Kota.</p>
    
    <p>Dari total <strong>{statistik['total_supervisi_akademik']} supervisi akademik</strong> dan 
    <strong>{statistik['total_supervisi_manajerial']} supervisi manajerial</strong> yang dilaksanakan, 
    diperoleh rata-rata nilai akademik sebesar <strong class="kualitas-{'unggul' if statistik['rata_akademik']>=91 else 'baik' if statistik['rata_akademik']>=76 else 'cukup'}">{statistik['rata_akademik']}</strong> 
    dan rata-rata nilai manajerial sebesar <strong>{statistik['rata_manajerial']}</strong>.</p>
    
    <p>Secara keseluruhan, kualitas pengelolaan madrasah di Kabupaten/Kota berada pada kategori 
    <strong class="kualitas-{'unggul' if rata_total>=91 else 'baik' if rata_total>=76 else 'cukup' if rata_total>=61 else 'kurang'}">{kualitas}</strong>.</p>
</div>

<!-- ANALISIS DATA -->
<h2>II. ANALISIS DATA</h2>

<h3>A. Statistik Umum</h3>
<table>
    <tr><th width="60%">Indikator</th><th>Jumlah</th></tr>
    <tr><td>Total Madrasah</td><td>{statistik['total_madrasah']}</td></tr>
    <tr><td>Total Guru</td><td>{statistik['total_guru']}</td></tr>
    <tr><td>Total Supervisi Akademik</td><td>{statistik['total_supervisi_akademik']}</td></tr>
    <tr><td>Total Supervisi Manajerial</td><td>{statistik['total_supervisi_manajerial']}</td></tr>
    <tr><td>Rata-rata Nilai Akademik</td><td>{statistik['rata_akademik']}</td></tr>
    <tr><td>Rata-rata Nilai Manajerial</td><td>{statistik['rata_manajerial']}</td></tr>
</table>

<h3>B. Distribusi Predikat Supervisi Akademik</h3>
<table>
    <tr><th>Predikat</th><th>Jumlah</th><th>Persentase</th></tr>
    <tr><td>A (Sangat Baik, ≥91)</td><td>{statistik['predikat_akademik']['A']}</td><td>{persen_a:.1f}%</td></tr>
    <tr><td>B (Baik, 76-90)</td><td>{statistik['predikat_akademik']['B']}</td><td>{persen_b:.1f}%</td></tr>
    <tr><td>C (Cukup, 61-75)</td><td>{statistik['predikat_akademik']['C']}</td><td>{persen_c:.1f}%</td></tr>
    <tr><td>D (Kurang, ≤60)</td><td>{statistik['predikat_akademik']['D']}</td><td>{persen_d:.1f}%</td></tr>
</table>

<h3>C. Rekap per Kecamatan</h3>
<table>
    <tr><th>Kecamatan</th><th>Jumlah Madrasah</th><th>Rata-rata Nilai</th><th>Status</th></tr>
    {tabel_kecamatan}
</table>

<!-- TEMUAN UTAMA -->
<h2>III. TEMUAN UTAMA</h2>
<ul>
    <li>Sebanyak <strong>{statistik['predikat_akademik']['A']} supervisi</strong> mencapai predikat A (Sangat Baik)</li>
    <li>Sebanyak <strong>{statistik['predikat_akademik']['D']} supervisi</strong> masih pada predikat D (Kurang) - memerlukan pendampingan intensif</li>
    <li>Kecamatan dengan nilai tertinggi: <strong>{statistik['rekap_kecamatan'][0]['nama'] if statistik['rekap_kecamatan'] else '-'}</strong> 
        ({statistik['rekap_kecamatan'][0]['nilai'] if statistik['rekap_kecamatan'] else '-'})</li>
    <li>Kecamatan dengan nilai terendah: <strong>{statistik['rekap_kecamatan'][-1]['nama'] if statistik['rekap_kecamatan'] else '-'}</strong> 
        ({statistik['rekap_kecamatan'][-1]['nilai'] if statistik['rekap_kecamatan'] else '-'})</li>
</ul>

<!-- REKOMENDASI -->
<h2>IV. REKOMENDASI</h2>
<ol>
    <li><strong>Penguatan Kompetensi Guru:</strong> Fokus pada indikator dengan nilai terendah melalui pelatihan dan pendampingan</li>
    <li><strong>Peningkatan Supervisi Manajerial:</strong> Intensifkan pendampingan pada madrasah dengan nilai di bawah 70</li>
    <li><strong>Evaluasi Berkala:</strong> Laksanakan evaluasi setiap triwulan untuk memantau perkembangan</li>
    <li><strong>Pemanfaatan Teknologi:</strong> Optimalkan penggunaan sistem informasi manajemen madrasah</li>
    <li><strong>Kemitraan dengan Komite:</strong> Libatkan komite madrasah dalam pengawasan mutu</li>
</ol>

<!-- KESIMPULAN -->
<h2>V. KESIMPULAN</h2>
<p>Berdasarkan hasil pengawasan periode {periode_nama} {tahun}, secara umum pengelolaan madrasah di Kabupaten/Kota 
berada pada kategori <strong>{kualitas}</strong>. Beberapa madrasah masih memerlukan pendampingan intensif, 
khususnya pada kecamatan dengan nilai di bawah standar.</p>

<p>Rekomendasi tindak lanjut telah disusun untuk menjadi acuan perbaikan mutu pendidikan madrasah secara berkelanjutan.</p>

<div class="signature">
    <p>Mengetahui,<br>
    Kepala Dinas Pendidikan Kabupaten/Kota</p>
    <br><br><br>
    <p><u>(Nama Kepala Dinas)</u><br>
    NIP. xxxxxxxxxxxxxxx</p>
</div>

<div class="footer">
    Laporan ini dihasilkan secara otomatis dari Sistem Pengawasan Madrasah<br>
    {datetime.now().strftime('%d %B %Y')}
</div>

</body>
</html>
    """
    
    return laporan