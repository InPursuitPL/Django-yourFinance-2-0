import re

from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from .models import Year, Month, Stash, Profile

class YearForm(forms.ModelForm):
    class Meta:
        model = Year
        fields = ('number',)


class MonthForm(forms.ModelForm):
    class Meta:
        model = Month
        fields = ('name',)

class MonthFullForm(forms.ModelForm):
    class Meta:
        model = Month
        fields = ('name', 'year')

class StashForm(forms.ModelForm):
    class Meta:
        model = Stash
        fields = ('name', 'amount')


class NameForm(forms.Form):
    name = forms.CharField(max_length=30, required=False)


class MonthlyCostsForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('existenceLevel', 'minimalLevel', 'standardLevel')


class RegistrationForm(forms.Form):
    username = forms.CharField(label='User name', max_length=30)
    email = forms.EmailField(label='E-mail')
    password1 = forms.CharField(label='Password',
                          widget=forms.PasswordInput())
    password2 = forms.CharField(label='Password (again)',
                        widget=forms.PasswordInput())

    def clean_password2(self):
        if 'password1' in self.cleaned_data:
            password1 = self.cleaned_data['password1']
            password2 = self.cleaned_data['password2']
            if password1 == password2:
                return password2
        raise forms.ValidationError('Passwords do not match.')

    def clean_username(self):
        username = self.cleaned_data['username']
        if not re.search(r'^\w+$', username):
            raise forms.ValidationError('Username can only contain\
alphanumeric characters and the underscore.')
        try:
            User.objects.get(username=username)
        except ObjectDoesNotExist:
            return username
        raise forms.ValidationError('Username is already taken.', code='invalid')
