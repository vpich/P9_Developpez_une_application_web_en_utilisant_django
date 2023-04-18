from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={"placeholder": "Nom d'utilisateur"}))
    password = forms.CharField(max_length=63, widget=forms.PasswordInput(attrs={"placeholder": "Mot de passe"}))


class SignupForm(UserCreationForm):
    password2 = forms.CharField(
        label="Confirmer mot de passe",
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', "placeholder": "Confirmer mot de passe"}),
        strip=False,
        help_text=_('Enter the same password as before, for verification.'),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({'placeholder': "Nom d'utilisateur"})
        self.fields["password1"].widget.attrs.update({'placeholder': "Mot de passe"})

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ("username", )

        labels = {
            "username": "Nom d'utilisateur"
        }
