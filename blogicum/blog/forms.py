from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    """Форма для создания и редактирования публикации."""
    class Meta:
        model = Post
        fields = ['title', 'text', 'image', 'is_published', 'pub_date', 'category', 'location']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите заголовок публикации',
            }),
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Введите текст публикации...',
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control-file',
            }),
            'is_published': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'pub_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
            }),
            'category': forms.Select(attrs={
                'class': 'form-control',
            }),
            'location': forms.Select(attrs={
                'class': 'form-control',
            }),
        }
        labels = {
            'title': 'Заголовок',
            'text': 'Текст',
            'image': 'Изображение',
            'is_published': 'Опубликовано',
            'pub_date': 'Дата публикации',
            'category': 'Категория',
            'location': 'Местоположение',
        }
