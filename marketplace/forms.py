from django import forms
from .models import BuySellPost, Rating


class PostForm(forms.ModelForm):
    class Meta:
        model = BuySellPost
        fields = ['post_type', 'title', 'product_name', 'category', 'quantity', 'price', 'unit', 'description', 'image', 'location', 'phone']
        widgets = {
            'post_type': forms.Select(attrs={'class': 'form-input'}),
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'পোস্টের শিরোনাম'}),
            'product_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'পণ্যের নাম'}),
            'category': forms.Select(attrs={'class': 'form-input'}),
            'quantity': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'পরিমাণ (যেমন: ১০০ কেজি)'}),
            'price': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'মূল্য (৳)'}),
            'unit': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'একক (কেজি/মণ/পিস)'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 4, 'placeholder': 'বিস্তারিত বর্ণনা'}),
            'location': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'অবস্থান'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'যোগাযোগ নম্বর'}),
        }


class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['score', 'comment']
        widgets = {
            'score': forms.RadioSelect(choices=[(i, f'{i} ★') for i in range(1, 6)]),
            'comment': forms.Textarea(attrs={'class': 'form-input', 'rows': 2, 'placeholder': 'মন্তব্য (ঐচ্ছিক)'}),
        }
