from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, label="Nom d'utilisateur")
    password = forms.CharField(max_length=63, widget=forms.PasswordInput, label="Mot de passe")
    password_check = forms.CharField(max_length=63, widget=forms.PasswordInput, label="Vérification de mot de passe")
