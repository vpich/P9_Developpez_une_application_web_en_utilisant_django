from django import forms

from . import models


class TicketForm(forms.ModelForm):
    class Meta:
        model = models.Ticket
        fields = ["title",
                  "description",
                  "image"]

        labels = {
            "title": "Titre"
        }


class ReviewForm(forms.ModelForm):
    CHOICES = [(number, number) for number in range(6)]
    rating = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect(), label="Note")

    class Meta:
        model = models.Review
        fields = ["headline",
                  "rating",
                  "body"]
        labels = {
            "headline": "Titre",
            "body": "Commentaire"
        }


class UserFollowsForm(forms.ModelForm):
    class Meta:
        model = models.UserFollows
        fields = ["followed_user", ]

        labels = {
            "followed_user": "Nom d'utilisateur"
        }

        widgets = {
            "followed_user": forms.TextInput(attrs={
                'placeholder': "Nom d'utilisateur"
            })
        }
