from django import forms
from django.forms import ModelForm
from main.models import Player

text_input_class = "w-full px-3 py-2 bg-background border border-gray-200 rounded-lg text-primary focus:outline-none focus:ring-2 focus:ring-accent"
select_input_class = "w-full px-3 py-2 bg-background border border-gray-200 rounded-lg text-primary focus:outline-none focus:ring-2 focus:ring-accent"

class PlayerForm(ModelForm):
    class Meta:
        model = Player
        fields = ["name", "date_of_birth", "country", "bio", "category", "status", "thumbnail", "world_rank", "partner", "is_featured"]

        widgets = {
            'name': forms.TextInput(attrs={'class': text_input_class, 'placeholder': 'Nama lengkap pemain'}),
            'date_of_birth': forms.DateInput(attrs={'class': text_input_class, 'type': 'date'}),
            'country': forms.Select(attrs={'class': select_input_class}),
            'category': forms.Select(attrs={'class': select_input_class}),
            'status': forms.Select(attrs={'class': select_input_class}),
            'thumbnail': forms.URLInput(attrs={'class': text_input_class, 'placeholder': 'https://example.com/image.jpg'}),
            'world_rank': forms.NumberInput(attrs={'class': text_input_class, 'placeholder': 'cth: 1'}),
            'partner': forms.Select(attrs={'class': select_input_class}),
            'bio': forms.Textarea(attrs={'class': text_input_class, 'rows': 4, 'placeholder': 'Biografi singkat pemain...'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'h-4 w-4 rounded border-gray-300 text-accent focus:ring-accent'}),
        }

        labels = {
            'name': 'Nama Lengkap',
            'date_of_birth': 'Tanggal Lahir',
            'country': 'Negara',
            'category': 'Kategori',
            'thumbnail': 'Link Foto Profil (URL)',
            'world_rank': 'Peringkat Dunia',
            'partner': 'Partner (jika ganda)',
            'bio': 'Biografi Singkat',
            'is_featured': 'Jadikan Pemain Unggulan?',
        }