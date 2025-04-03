from django import forms

class ProfileForm(forms.Form):
    avatar = forms.FileField()
    username = forms.CharField(label = "Username")
    