from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, label="Nom d'utilisateur")
    password = forms.CharField(max_length=63, widget=forms.PasswordInput, label="Mot de passe")


class SignupForm(UserCreationForm):
    password2 = forms.CharField(
        label="Confirmer mot de passe",
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        strip=False,
        help_text=_('Enter the same password as before, for verification.'),
    )

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ("username", )

        labels = {
            "username": "Nom d'utilisateur"
        }
