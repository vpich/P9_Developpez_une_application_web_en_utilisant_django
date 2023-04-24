from itertools import chain
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.db.models import Q
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.db import IntegrityError

from authentication.models import User
from . import forms, models


ERROR_MESSAGE = "Saisie invalide."
DELETE_MESSAGE = "Suppression effectuée."


def owner_permission(request, element):
    if request.user != element.user:
        exception = "Vous ne pouvez pas modifier ou supprimer un post dont vous n'êtes pas le créateur."
        raise PermissionDenied(exception)


def permission_denied_view(request, exception):
    return render(request,
                  "review/permission_denied.html",
                  {"exception": exception})


def ticket_already_responded(ticket):
    if models.Review.objects.filter(ticket=ticket):
        message = "Vous ne pouvez pas répondre à un ticket qui a déjà obtenu une réponse."
        raise PermissionDenied(message)


def page_not_found_view(request, exception):
    return render(request,
                  "review/page_not_found.html",
                  {"exception": exception})


class Feed(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request):

        follows = models.UserFollows.objects.filter(user=request.user.id)
        tickets = models.Ticket.objects.filter(
            Q(user__in=follows.values("followed_user")) |
            Q(user=request.user.id)
        )

        own_tickets = models.Ticket.objects.filter(user=request.user.id)
        reviews = models.Review.objects.filter(
            Q(user__in=follows.values("followed_user")) |
            Q(ticket__in=own_tickets)
        )

        posts = sorted(
            chain(tickets, reviews),
            key=lambda post: post.time_created,
            reverse=True
        )

        paginator = Paginator(posts, 5)

        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        tickets_responded = []
        for ticket in tickets:
            all_reviews = models.Review.objects.filter(ticket=ticket)
            if all_reviews:
                tickets_responded.append(ticket.id)

        return render(request,
                      "review/feed.html",
                      {"page_obj": page_obj,
                       "tickets_responded": tickets_responded})


class PostsPage(LoginRequiredMixin, View):
    login_url = "/login/"
    ticket_form = models.Ticket
    review_form = models.Review

    def get(self, request):
        tickets = self.ticket_form.objects.filter(user=request.user)
        reviews = self.review_form.objects.filter(user=request.user)

        posts = sorted(
            chain(tickets, reviews),
            key=lambda post: post.time_created,
            reverse=True,
        )

        paginator = Paginator(posts, 5)

        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        return render(request,
                      "review/posts.html",
                      {"page_obj": page_obj})


class CreateTicket(LoginRequiredMixin, View):
    login_url = "/login/"
    form = forms.TicketForm

    def get(self, request):
        form = self.form()
        return render(request,
                      "review/create_ticket.html",
                      {"form": form})

    def post(self, request):
        form = self.form(request.POST, request.FILES)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            message = "Votre demande de critique a été créée."
            messages.add_message(request, messages.SUCCESS, message)
            return redirect("feed")
        message = "Vous ne pouvez pas ajouter de fichiers qui ne soient pas au format image."
        messages.add_message(request, messages.ERROR, message)
        return redirect("create-ticket")


class UpdateTicket(LoginRequiredMixin, View):
    login_url = "/login/"
    form = forms.TicketForm

    def get(self, request, ticket_id):
        ticket = get_object_or_404(models.Ticket, id=ticket_id)
        owner_permission(request, ticket)
        form = self.form(instance=ticket)
        return render(request,
                      "review/update_ticket.html",
                      {"form": form,
                       "ticket": ticket})

    def post(self, request, ticket_id):
        ticket = get_object_or_404(models.Ticket, id=ticket_id)
        form = self.form(request.POST, request.FILES)
        if form.is_valid():
            ticket.title = form.cleaned_data["title"]
            ticket.description = form.cleaned_data["description"]
            ticket.image = form.cleaned_data["image"]
            ticket.save()
            message = "La mise à jour de votre demande a été prise en compte."
            messages.add_message(request, messages.SUCCESS, message)
            return redirect("posts")
        messages.add_message(request, messages.ERROR, ERROR_MESSAGE)
        return redirect("update-ticket", ticket_id)


class DeleteTicket(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request, ticket_id):
        ticket = get_object_or_404(models.Ticket, id=ticket_id)
        owner_permission(request, ticket)
        return render(request,
                      "review/delete_ticket.html",
                      {"ticket": ticket})

    def post(self, request, ticket_id):
        ticket = get_object_or_404(models.Ticket, id=ticket_id)
        ticket.delete()
        messages.add_message(request, messages.SUCCESS, DELETE_MESSAGE)
        return redirect("posts")


class CreateReview(LoginRequiredMixin, View):
    login_url = "/login/"
    review_form = forms.ReviewForm
    ticket_form = forms.TicketForm

    def get(self, request):
        review_form = self.review_form()
        ticket_form = self.ticket_form()
        return render(request,
                      "review/create_review.html",
                      {"review_form": review_form,
                       "ticket_form": ticket_form})

    def post(self, request):
        review_form = self.review_form(request.POST)
        ticket_form = self.ticket_form(request.POST, request.FILES)
        if all([ticket_form.is_valid(), review_form.is_valid()]):
            ticket = ticket_form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            review = review_form.save(commit=False)
            review.user = request.user
            review.ticket = ticket
            review.save()
            message = "Votre critique a été créée."
            messages.add_message(request, messages.SUCCESS, message)
            return redirect("feed")
        messages.add_message(request, messages.ERROR, ERROR_MESSAGE)
        return redirect("create-review")


class CreateReviewResponse(LoginRequiredMixin, View):
    login_url = "/login/"
    form = forms.ReviewForm
    model = models.Ticket

    def get(self, request, ticket_id):
        form = self.form()
        ticket = self.model.objects.get(id=ticket_id)
        ticket_already_responded(ticket)
        return render(request,
                      "review/create_review_response.html",
                      {"form": form,
                       "ticket": ticket})

    def post(self, request, ticket_id):
        form = self.form(request.POST)
        ticket = self.model.objects.get(id=ticket_id)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.ticket = ticket
            review.save()
            message = "Votre critique a été créée."
            messages.add_message(request, messages.SUCCESS, message)
            return redirect("feed")
        messages.add_message(request, messages.ERROR, ERROR_MESSAGE)
        return redirect("create-review-response")


class UpdateReview(LoginRequiredMixin, View):
    login_url = "/login/"
    form = forms.ReviewForm

    def get(self, request, review_id):
        review = get_object_or_404(models.Review, id=review_id)
        owner_permission(request, review)
        form = self.form(instance=review)
        return render(request,
                      "review/update_review.html",
                      {"form": form,
                       "review": review})

    def post(self, request, review_id):
        review = get_object_or_404(models.Review, id=review_id)
        form = self.form(request.POST)
        if form.is_valid():
            review.rating = form.cleaned_data["rating"]
            review.headline = form.cleaned_data["headline"]
            review.body = form.cleaned_data["body"]
            review.save()
            message = "La mise à jour de votre critique a été prise en compte."
            messages.add_message(request, messages.SUCCESS, message)
            return redirect("posts")
        messages.add_message(request, messages.ERROR, ERROR_MESSAGE)
        return redirect("update-review", review_id)


class DeleteReview(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request, review_id):
        review = get_object_or_404(models.Review, id=review_id)
        owner_permission(request, review)
        return render(request,
                      "review/delete_review.html",
                      {"review": review})

    def post(self, request, review_id):
        review = get_object_or_404(models.Review, id=review_id)
        review.delete()
        messages.add_message(request, messages.SUCCESS, DELETE_MESSAGE)
        return redirect("posts")


class FollowPage(LoginRequiredMixin, View):
    login_url = "/login/"
    form = forms.FollowForm

    def get(self, request):
        form = self.form()
        follows = models.UserFollows.objects.filter(user=request.user)
        followers = models.UserFollows.objects.filter(followed_user=request.user)

        return render(request,
                      "review/follows.html",
                      {"follows": follows,
                       "form": form,
                       "followers": followers})

    def post(self, request):
        form = self.form(request.POST)
        if form.is_valid():
            follow = models.UserFollows()
            follow.user = request.user
            followed_name = form.cleaned_data["followed_name"]
            if follow.user.username == followed_name:
                message = "Vous ne pouvez pas vous suivre vous même."
                messages.add_message(request, messages.ERROR, message)
            else:
                try:
                    followed_user = User.objects.get(username=followed_name)
                    follow.followed_user = followed_user
                    follow.save()
                    message = f"Vous avez ajouté {follow.followed_user} à votre liste de suivi."
                    messages.add_message(request, messages.SUCCESS, message)
                except User.DoesNotExist:
                    message = "Aucun user ne correspond à ce nom."
                    messages.add_message(request, messages.ERROR, message)
                except IntegrityError:
                    message = "Vous suivez déjà cet utilisateur."
                    messages.add_message(request, messages.ERROR, message)

        follows = models.UserFollows.objects.filter(user=request.user)
        followers = models.UserFollows.objects.filter(followed_user=request.user)

        return render(request,
                      "review/follows.html",
                      {"follows": follows,
                       "form": form,
                       "followers": followers})


class DeleteFollow(LoginRequiredMixin, View):
    login_url = "/login/"
    model = models.UserFollows

    def get(self, request, follow_id):
        follow = self.model.objects.get(id=follow_id)
        owner_permission(request, follow)

        return render(request,
                      "review/delete_follow.html",
                      {"follow": follow})

    def post(self, request, follow_id):
        follow = self.model.objects.get(id=follow_id)
        follow.delete()
        messages.add_message(request, messages.SUCCESS, DELETE_MESSAGE)
        return redirect("followed-users")
