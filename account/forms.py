from django import forms

class LoginForm(forms.Form):
    '''User Login forms'''
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)