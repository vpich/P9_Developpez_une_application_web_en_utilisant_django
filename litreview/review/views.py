from itertools import chain
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied, \
    ObjectDoesNotExist, FieldError, BadRequest
from django.contrib import messages
from django.db.models import Q

from .models import Ticket, Review, UserFollows
from .forms import TicketForm, ReviewForm, FollowForm

ERROR_MESSAGE = "Saisie invalide."
DELETE_MESSAGE = "Suppression effectuée."


def permission_denied_view(request, exception):
    return render(request,
                  "review/permission_denied.html",
                  {"exception": exception})


def page_not_found_view(request, exception):
    return render(request,
                  "review/page_not_found.html",
                  {"exception": exception})


def owner_permission(request, element):
    if request.user != element.user:
        exception = "Vous ne pouvez pas modifier " \
                    "ou supprimer un post dont vous n'êtes pas le créateur."
        raise PermissionDenied(exception)


def ticket_already_responded(ticket):
    if Review.objects.filter(ticket=ticket):
        message = "Vous ne pouvez pas répondre à un ticket" \
                  " qui a déjà obtenu une réponse."
        raise PermissionDenied(message)


def get_own_posts(user):
    tickets = Ticket.objects.filter(user=user.id)
    reviews = Review.objects.filter(user=user.id)
    own_posts = sorted(
        chain(tickets, reviews),
        key=lambda post: post.time_created,
        reverse=True,
    )
    return own_posts


def get_viewable_tickets(user):
    follows = UserFollows.objects.filter(user=user.id)
    tickets = Ticket.objects.filter(
        Q(user=user.id) |
        Q(user__in=follows.values("followed_user"))
    )
    return tickets


def get_viewable_reviews(user):
    own_tickets = Ticket.objects.filter(user=user.id)
    follows = UserFollows.objects.filter(user=user.id)
    reviews = Review.objects.filter(
        Q(user=user.id) |
        Q(user__in=follows.values("followed_user")) |
        Q(ticket__in=own_tickets)
    )
    return reviews


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
    template_name = "review/feed.html"

    def get(self, request):
        tickets = get_viewable_tickets(request.user)
        reviews = get_viewable_reviews(request.user)

        posts = sorted(
            chain(tickets, reviews),
            key=lambda post: post.time_created,
            reverse=True
        )

        page_obj = pagination(request, posts)
        tickets_responded = get_tickets_responded(posts)

        context = {"page_obj": page_obj,
                   "tickets_responded": tickets_responded}

        return render(request,
                      self.template_name,
                      context)


class PostsPage(LoginRequiredMixin, View):
    template_name = "review/posts.html"

    def get(self, request):
        posts = get_own_posts(request.user)
        page_obj = pagination(request, posts)

        context = {"page_obj": page_obj}

        return render(request,
                      self.template_name,
                      context)


class CreateTicket(LoginRequiredMixin, View):
    template_name = "review/create_ticket.html"
    form = TicketForm
    model = Ticket

    def get(self, request):
        form = self.form()
        context = {"form": form}
        return render(request,
                      self.template_name,
                      context)

    def post(self, request):
        form = self.form(request.POST, request.FILES)
        if form.is_valid():
            self.model.objects.create(request.user, form)
            message = "Votre demande de critique a été créée."
            messages.add_message(request, messages.SUCCESS, message)
            return redirect("feed")
        messages.add_message(request, messages.ERROR, ERROR_MESSAGE)
        return redirect("create-ticket")


class UpdateTicket(LoginRequiredMixin, View):
    template_name = "review/update_ticket.html"
    form = TicketForm

    def get(self, request, ticket_id):
        ticket = get_object_or_404(Ticket, id=ticket_id)
        owner_permission(request, ticket)
        form = self.form(instance=ticket)

        context = {"form": form, "ticket": ticket}
        return render(request,
                      self.template_name,
                      context)

    def post(self, request, ticket_id):
        ticket = get_object_or_404(Ticket, id=ticket_id)
        form = self.form(request.POST, request.FILES)
        if form.is_valid():
            Ticket.objects.update(ticket, form)
            message = "La mise à jour de votre demande a été prise en compte."
            messages.add_message(request, messages.SUCCESS, message)
            return redirect("posts")
        messages.add_message(request, messages.ERROR, ERROR_MESSAGE)
        return redirect("update-ticket", ticket_id)


class DeleteTicket(LoginRequiredMixin, View):
    template_name = "review/delete_ticket.html"
    model = Ticket

    def get(self, request, ticket_id):
        ticket = get_object_or_404(self.model, id=ticket_id)
        owner_permission(request, ticket)
        context = {"ticket": ticket}
        return render(request,
                      self.template_name,
                      context)

    def post(self, request, ticket_id):
        ticket = get_object_or_404(self.model, id=ticket_id)
        ticket.delete()
        messages.add_message(request, messages.SUCCESS, DELETE_MESSAGE)
        return redirect("posts")


class CreateReview(LoginRequiredMixin, View):
    template_name = "review/create_review.html"
    review_form = ReviewForm
    ticket_form = TicketForm
    ticket_model = Ticket
    review_model = Review

    def get(self, request):
        context = {"review_form": self.review_form(),
                   "ticket_form": self.ticket_form()}
        return render(request,
                      self.template_name,
                      context)

    def post(self, request):
        review_form = self.review_form(request.POST)
        ticket_form = self.ticket_form(request.POST, request.FILES)
        if all([ticket_form.is_valid(), review_form.is_valid()]):
            ticket = self.ticket_model.objects.create(
                request.user,
                ticket_form
            )
            self.review_model.objects.create(
                request.user,
                review_form,
                ticket
            )
            message = "Votre critique a été créée."
            messages.add_message(request, messages.SUCCESS, message)
            return redirect("feed")
        messages.add_message(request, messages.ERROR, ERROR_MESSAGE)
        return redirect("create-review")


class CreateReviewResponse(LoginRequiredMixin, View):
    template_name = "review/create_review_response.html"
    form = ReviewForm
    ticket_model = Ticket
    review_model = Review

    def get(self, request, ticket_id):
        form = self.form()
        ticket = self.ticket_model.objects.get(id=ticket_id)
        ticket_already_responded(ticket)
        context = {"form": form, "ticket": ticket}
        return render(request,
                      self.template_name,
                      context)

    def post(self, request, ticket_id):
        form = self.form(request.POST)
        ticket = self.ticket_model.objects.get(id=ticket_id)
        if form.is_valid():
            self.review_model.objects.create(request.user, form, ticket)
            message = "Votre critique a été créée."
            messages.add_message(request, messages.SUCCESS, message)
            return redirect("feed")
        messages.add_message(request, messages.ERROR, ERROR_MESSAGE)
        return redirect("create-review-response", ticket_id)


class UpdateReview(LoginRequiredMixin, View):
    template_name = "review/update_review.html"
    form = ReviewForm
    model = Review

    def get(self, request, review_id):
        review = get_object_or_404(Review, id=review_id)
        owner_permission(request, review)
        form = self.form(instance=review)
        context = {"form": form, "review": review}
        return render(request,
                      self.template_name,
                      context)

    def post(self, request, review_id):
        review = get_object_or_404(Review, id=review_id)
        form = self.form(request.POST)
        if form.is_valid():
            self.model.objects.update(review, form)
            message = "La mise à jour de votre critique a été prise en compte."
            messages.add_message(request, messages.SUCCESS, message)
            return redirect("posts")
        messages.add_message(request, messages.ERROR, ERROR_MESSAGE)
        return redirect("update-review", review_id)


class DeleteReview(LoginRequiredMixin, View):
    template_name = "review/delete_review.html"
    model = Review

    def get(self, request, review_id):
        review = get_object_or_404(self.model, id=review_id)
        owner_permission(request, review)
        context = {"review": review}
        return render(request,
                      self.template_name,
                      context)

    def post(self, request, review_id):
        review = get_object_or_404(self.model, id=review_id)
        review.delete()
        messages.add_message(request, messages.SUCCESS, DELETE_MESSAGE)
        return redirect("posts")


class FollowPage(LoginRequiredMixin, View):
    template_name = "review/follows.html"
    form = FollowForm
    model = UserFollows

    def get(self, request):
        form = self.form()
        follows = self.model.objects.filter(user=request.user)
        followers = self.model.objects.filter(followed_user=request.user)
        context = {"follows": follows,
                   "form": form,
                   "followers": followers}
        return render(request,
                      self.template_name,
                      context)

    def post(self, request):
        form = self.form(request.POST)
        message = ERROR_MESSAGE
        message_success = None
        if form.is_valid():
            follow = self.model.objects.create(request.user, form)
            if follow == FieldError:
                message = "Vous ne pouvez pas vous suivre vous même."
            elif type(follow) == self.model:
                message_success = f"Vous avez ajouté {follow.followed_user} " \
                                  f"à votre liste de suivi."
            elif follow == ObjectDoesNotExist:
                message = "Aucun utilisateur ne correspond à ce nom."
            elif follow == BadRequest:
                message = "Vous suivez déjà cet utilisateur."
        if message_success:
            messages.add_message(request, messages.SUCCESS, message_success)
        else:
            messages.add_message(request, messages.ERROR, message)

        return redirect("followed-users")


class DeleteFollow(LoginRequiredMixin, View):
    template_name = "review/delete_follow.html"
    model = UserFollows

    def get(self, request, follow_id):
        follow = get_object_or_404(self.model, id=follow_id)
        owner_permission(request, follow)
        context = {"follow": follow}
        return render(request,
                      self.template_name,
                      context)

    def post(self, request, follow_id):
        follow = get_object_or_404(self.model, id=follow_id)
        follow.delete()
        messages.add_message(request, messages.SUCCESS, DELETE_MESSAGE)
        return redirect("followed-users")
