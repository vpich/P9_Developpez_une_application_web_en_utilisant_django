from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from django.db import models, IntegrityError
from django.core.exceptions import ObjectDoesNotExist, FieldError, BadRequest

from authentication.models import User


class TicketManager(models.Manager):
    def create(self, user, form):
        ticket = form.save(commit=False)
        ticket.user = user
        ticket.save()
        return ticket

    def update(self, ticket, form):
        ticket.title = form.cleaned_data["title"]
        ticket.description = form.cleaned_data["description"]
        ticket.image = form.cleaned_data["image"]
        ticket.save()
        return ticket


class Ticket(models.Model):
    title = models.CharField(max_length=128)
    description = models.TextField(max_length=2048, blank=True)
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    image = models.ImageField(null=True, blank=True)
    time_created = models.DateTimeField(auto_now_add=True)

    objects = TicketManager()


class ReviewManager(models.Manager):
    def create(self, user, form, ticket):
        review = form.save(commit=False)
        review.user = user
        review.ticket = ticket
        review.save()
        return review

    def update(self, review, form):
        review.rating = form.cleaned_data["rating"]
        review.headline = form.cleaned_data["headline"]
        review.body = form.cleaned_data["body"]
        review.save()
        return review


class Review(models.Model):
    ticket = models.ForeignKey(to=Ticket, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(
        # validates that rating must be between 0 and 5
        validators=[MinValueValidator(0), MaxValueValidator(5)])
    headline = models.CharField(max_length=128)
    body = models.TextField(max_length=8192, blank=True)
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    time_created = models.DateTimeField(auto_now_add=True)

    objects = ReviewManager()


class UserFollowsManager(models.Manager):
    def create(self, user, form):
        follow = UserFollows()
        follow.user = user
        followed_name = form.cleaned_data["followed_name"]
        if follow.user.username == followed_name:
            return FieldError
        else:
            try:
                followed_user = User.objects.get(username=followed_name)
                follow.followed_user = followed_user
                follow.save()
            except User.DoesNotExist:
                return ObjectDoesNotExist
            except IntegrityError:
                return BadRequest
            return follow


class UserFollows(models.Model):
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="following"
    )
    followed_user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="followed_by"
    )

    class Meta:
        # ensures we don't get multiple UserFollows instances
        # for unique user-user_followed pairs
        unique_together = ('user', 'followed_user', )

    objects = UserFollowsManager()
