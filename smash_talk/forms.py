from django import forms
from .models import Post, Comment

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'category', 'content']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Judul postingan...'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Tulis konten postingan di sini...',
                'rows': 5
            }),
        }
        labels = {
            'title': 'Judul',
            'category': 'Kategori',
            'content': 'Konten'
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Tulis komentar Anda di sini...',
                'rows': 3
            }),
        }
        labels = {
            'content': 'Komentar'
        }