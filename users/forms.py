from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User  

class CustomUserCreationForm(UserCreationForm):  
    class Meta:
        model = User
        fields = ('username', 'email', 'role', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].choices = [
            (key, value) for key, value in self.fields['role'].choices if key != 'admin'
        ]