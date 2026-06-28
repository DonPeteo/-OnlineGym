from django import forms # f
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Review

class RegisterForm(UserCreationForm):
    email = forms.EmailField() # f

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):

        email = self.cleaned_data['email']

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "A user with this email already exists."
            )

        return email
        

class ReviewForm(forms.ModelForm):

    class Meta:
        model = Review
        fields = ['rating', 'comment']

        widgets = {
            'rating': forms.NumberInput(attrs={
                'min': 1,
                'max': 5,
                'class': 'w-full border rounded-xl p-2'
            }),
            'comment': forms.Textarea(attrs={
                'rows': 4,
                'class': 'w-full border rounded-xl p-2'
            }),
        }