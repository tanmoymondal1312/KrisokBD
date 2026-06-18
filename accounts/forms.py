from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=100, required=True,
        widget=forms.TextInput(attrs={'placeholder': 'আপনার নাম', 'class': 'form-input'})
    )
    phone = forms.CharField(
        max_length=20, required=True,
        widget=forms.TextInput(attrs={'placeholder': '01XXXXXXXXX', 'class': 'form-input'})
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={'placeholder': 'ইমেইল (ঐচ্ছিক)', 'class': 'form-input'})
    )
    user_type = forms.ChoiceField(
        choices=User.USER_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-input'})
    )

    class Meta:
        model = User
        fields = ['first_name', 'username', 'phone', 'email', 'user_type', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'ইউজারনেম', 'class': 'form-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'placeholder': 'পাসওয়ার্ড', 'class': 'form-input'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'পাসওয়ার্ড নিশ্চিত করুন', 'class': 'form-input'})


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'ইউজারনেম বা ফোন', 'class': 'form-input'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'পাসওয়ার্ড', 'class': 'form-input'})
    )


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone', 'email', 'user_type', 'district', 'address', 'avatar']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
            'phone': forms.TextInput(attrs={'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-input'}),
            'user_type': forms.Select(attrs={'class': 'form-input'}),
            'district': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'জেলা'}),
            'address': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'ঠিকানা'}),
        }
