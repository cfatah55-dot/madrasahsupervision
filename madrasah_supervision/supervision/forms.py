from django import forms
from .models import HasilSupervisi, TagihanPengawas, Madrasah, Guru
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class HasilSupervisiForm(forms.ModelForm):
    class Meta:
        model = HasilSupervisi
        fields = ['guru', 'madrasah', 'tanggal', 'semester', 'tahun_ajaran', 
                  'rekomendasi', 'tindak_lanjut', 'file_pendukung']
        widgets = {
            'tanggal': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'semester': forms.Select(attrs={'class': 'form-control'}),
            'tahun_ajaran': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '2024/2025'}),
            'guru': forms.Select(attrs={'class': 'form-control'}),
            'madrasah': forms.Select(attrs={'class': 'form-control'}),
            'rekomendasi': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'tindak_lanjut': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'file_pendukung': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'madrasah' in self.data:
            try:
                madrasah_id = int(self.data.get('madrasah'))
                self.fields['guru'].queryset = Guru.objects.filter(madrasah_id=madrasah_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['guru'].queryset = self.instance.madrasah.gurus.all()

class TagihanPengawasForm(forms.ModelForm):
    class Meta:
        model = TagihanPengawas
        fields = ['nomor_tagihan', 'madrasah', 'jatuh_tempo', 'deskripsi', 'jumlah', 'file_tagihan']
        widgets = {
            'nomor_tagihan': forms.TextInput(attrs={'class': 'form-control'}),
            'madrasah': forms.Select(attrs={'class': 'form-control'}),
            'jatuh_tempo': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'deskripsi': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'jumlah': forms.NumberInput(attrs={'class': 'form-control'}),
            'file_tagihan': forms.FileInput(attrs={'class': 'form-control'}),
        }

class ImportDataForm(forms.Form):
    file = forms.FileField(label='File Excel', help_text='Format: .xlsx, .xls')
    
class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']