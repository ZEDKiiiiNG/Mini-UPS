from django import forms
from datetime import datetime

from django.forms import TextInput, DateInput, TimeInput

from . import models

calendar_widget = forms.widgets.DateInput(attrs={'class': 'date-pick'}, format='%m/%d/%Y')
time_widget = forms.widgets.TimeInput(attrs={'class': 'time-pick'})
valid_time_formats = ['%H:%M', '%I:%M%p', '%I:%M %p']

class UserForm(forms.Form):
    username = forms.CharField(label="username", max_length=128)
    password = forms.CharField(label="password", max_length=256, widget=forms.PasswordInput)


class RegisterForm(forms.Form):
    username = forms.CharField(label="username", max_length=128,
                               widget=forms.TextInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(label="password", max_length=256,
                                widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label="password_confirmed", max_length=256,
                                widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label="email", widget=forms.EmailInput(attrs={'class': 'form-control'}))
class ChangeDestinationForm(forms.Form):
    newDestX = forms.IntegerField(label="New Destination X",widget=forms.NumberInput)
    newDestY = forms.IntegerField(label="New Destination Y",widget=forms.NumberInput)
class SearchPackageForm(forms.Form):
    pkgId = forms.IntegerField(label="Please eneter the package ID",widget=forms.NumberInput)
