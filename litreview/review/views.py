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
from .models import Ticket, Review, UserFollows
from .forms import TicketForm, ReviewForm, FollowForm


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
    if Review.objects.filter(ticket=ticket):
        message = "Vous ne pouvez pas répondre à un ticket qui a déjà obtenu une réponse."
        raise PermissionDenied(message)


def page_not_found_view(request, exception):
    return render(request,
                  "review/page_not_found.html",
                  {"exception": exception})


def get_own_posts(request):
    tickets = Ticket.objects.filter(user=request.user.id)
    reviews = Review.objects.filter(ticket__in=tickets)

    own_posts = chain(tickets, reviews)

    return own_posts


def get_followed_users_posts(request):
    follows = UserFollows.objects.filter(user=request.user.id)
    tickets = Ticket.objects.filter(user__in=follows.values("followed_user"))
    reviews = Review.objects.filter(user__in=follows.values("followed_user"))

    followed_posts = chain(tickets, reviews)

    return followed_posts


def get_tickets_responded(posts):
    tickets_responded = []
    tickets = []

    for post in posts:
        if type(post) == Ticket:
            tickets.append(post)
    for ticket in tickets:
        all_reviews = Review.objects.filter(ticket=ticket)
        if all_reviews:
            tickets_responded.append(ticket.id)
    return tickets_responded


def pagination(request, posts):
    paginator = Paginator(posts, 5)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return page_obj


class Feed(LoginRequiredMixin, View):
    login_url = "/login/"
    "review/feed.html"

    def get(self, request):
        own_posts = get_own_posts(request)
        followed_users_posts = get_followed_users_posts(request)

        posts = sorted(
            chain(own_posts, followed_users_posts),
            key=lambda post: post.time_created,
            reverse=True
        )

        page_obj = pagination(request, posts)
        tickets_responded = get_tickets_responded(posts)

        return render(request,
                      "review/feed.html",
                      {"page_obj": page_obj,
                       "tickets_responded": tickets_responded})


class PostsPage(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request):
        posts = get_own_posts(request)

        posts = sorted(
            posts,
            key=lambda post: post.time_created,
            reverse=True,
        )

        page_obj = pagination(request, posts)

        return render(request,
                      "review/posts.html",
                      {"page_obj": page_obj})


# class CreateTicket(LoginRequiredMixin, CreateView):
#     model = models.Ticket
#     form_class = forms.TicketForm
#     template_name = "review/create_ticket.html"


class CreateTicket(LoginRequiredMixin, View):
    login_url = "/login/"
    form = TicketForm

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
        messages.add_message(request, messages.ERROR, ERROR_MESSAGE)
        return redirect("create-ticket")


class UpdateTicket(LoginRequiredMixin, View):
    login_url = "/login/"
    form = TicketForm

    def get(self, request, ticket_id):
        ticket = get_object_or_404(Ticket, id=ticket_id)
        owner_permission(request, ticket)
        form = self.form(instance=ticket)
        return render(request,
                      "review/update_ticket.html",
                      {"form": form,
                       "ticket": ticket})

    def post(self, request, ticket_id):
        ticket = get_object_or_404(Ticket, id=ticket_id)
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
        ticket = get_object_or_404(Ticket, id=ticket_id)
        owner_permission(request, ticket)
        return render(request,
                      "review/delete_ticket.html",
                      {"ticket": ticket})

    def post(self, request, ticket_id):
        ticket = get_object_or_404(Ticket, id=ticket_id)
        ticket.delete()
        messages.add_message(request, messages.SUCCESS, DELETE_MESSAGE)
        return redirect("posts")


class CreateReview(LoginRequiredMixin, View):
    login_url = "/login/"
    review_form = ReviewForm
    ticket_form = TicketForm

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
    form = ReviewForm
    model = Ticket

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
    form = ReviewForm

    def get(self, request, review_id):
        review = get_object_or_404(Review, id=review_id)
        owner_permission(request, review)
        form = self.form(instance=review)
        return render(request,
                      "review/update_review.html",
                      {"form": form,
                       "review": review})

    def post(self, request, review_id):
        review = get_object_or_404(Review, id=review_id)
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
        review = get_object_or_404(Review, id=review_id)
        owner_permission(request, review)
        return render(request,
                      "review/delete_review.html",
                      {"review": review})

    def post(self, request, review_id):
        review = get_object_or_404(Review, id=review_id)
        review.delete()
        messages.add_message(request, messages.SUCCESS, DELETE_MESSAGE)
        return redirect("posts")


class FollowPage(LoginRequiredMixin, View):
    login_url = "/login/"
    form = FollowForm

    def get(self, request):
        form = self.form()
        follows = UserFollows.objects.filter(user=request.user)
        followers = UserFollows.objects.filter(followed_user=request.user)

        return render(request,
                      "review/follows.html",
                      {"follows": follows,
                       "form": form,
                       "followers": followers})

    def post(self, request):
        form = self.form(request.POST)
        message = ERROR_MESSAGE
        message_success = None
        if form.is_valid():
            follow = UserFollows()
            follow.user = request.user
            followed_name = form.cleaned_data["followed_name"]
            if follow.user.username == followed_name:
                message = "Vous ne pouvez pas vous suivre vous même."
            else:
                try:
                    followed_user = User.objects.get(username=followed_name)
                    follow.followed_user = followed_user
                    follow.save()
                    message_success = f"Vous avez ajouté {follow.followed_user} à votre liste de suivi."
                except User.DoesNotExist:
                    message = "Aucun utilisateur ne correspond à ce nom."
                except IntegrityError:
                    message = "Vous suivez déjà cet utilisateur."
        if message_success:
            messages.add_message(request, messages.SUCCESS, message_success)
        else:
            messages.add_message(request, messages.ERROR, message)

        follows = UserFollows.objects.filter(user=request.user)
        followers = UserFollows.objects.filter(followed_user=request.user)

        return render(request,
                      "review/follows.html",
                      {"follows": follows,
                       "form": form,
                       "followers": followers})


class DeleteFollow(LoginRequiredMixin, View):
    login_url = "/login/"
    model = UserFollows

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
