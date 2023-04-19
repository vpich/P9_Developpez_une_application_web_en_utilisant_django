from django import forms
from django.forms.widgets import FileInput

from . import models


class TicketForm(forms.ModelForm):
    image = forms.FileField(widget=forms.FileInput(attrs={
        "class": "test",
        }
    ))

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


class FollowForm(forms.Form):
    followed_name = forms.CharField(label="Nom d'utilisateur",
                                    widget=forms.TextInput(attrs={"placeholder": "Nom d'utilisateur"}))
