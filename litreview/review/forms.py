from django import forms

from . import models


class TicketForm(forms.ModelForm):
    class Meta:
        model = models.Ticket
        fields = ["title",
                  "description",
                  "image"]


class ReviewForm(forms.ModelForm):
    class Meta:
        model = models.Review
        fields = ["ticket",
                  "rating",
                  "headline",
                  "body"]


class UserFollowsForm(forms.ModelForm):
    class Meta:
        model = models.UserFollows
        fields = ["followed_user", ]

