from django import forms
from .models import Contact
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from userprofile.models import Customer


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['full_name', 'email', 'message', 'screenshot']


class CustomerForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']        


class Profileform(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'pix']
