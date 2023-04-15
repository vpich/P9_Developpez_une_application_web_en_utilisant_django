from itertools import chain
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views import View
from django.utils.decorators import method_decorator
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.db.models import CharField, Value

from . import forms, models


def feed(request, feed_type):
    tickets = models.Ticket.objects.filter(title__exact='')
    reviews = models.Review.objects.filter(headline__exact='')
    if feed_type == 1:
        follows = models.UserFollows.objects.filter(user=request.user.id)
        tickets = models.Ticket.objects.filter(
            user__in=follows.values("followed_user")
        )

        reviews = models.Review.objects.filter(
            user__in=follows.values("followed_user")
        )

    elif feed_type == 2:
        tickets = models.Ticket.objects.filter(user=request.user.id)

    elif feed_type == 3:
        own_tickets = models.Ticket.objects.filter(user=request.user.id)
        reviews = models.Review.objects.filter(ticket__in=own_tickets)

    tickets = tickets.annotate(content_type=Value("TICKET", CharField()))
    reviews = reviews.annotate(content_type=Value("REVIEW", CharField()))

    posts = sorted(
        chain(tickets, reviews),
        key=lambda post: post.time_created,
        reverse=True
    )

    return posts

# class LoginRequiredMixin(object):
#     @method_decorator(login_required)
#     def dispatch(self, *args, **kwargs):
#         return super(LoginRequiredMixin, self).dispatch(*args, **kwargs)


# class Home(View):
#     def get(self, request):
#         return render(request,
#                       "review/home.html")
#
#     def post(self, request):
#         logout_user(request)
#         return redirect("login")

@login_required(login_url="login")
def home(request):
    posts_followed = feed(request, 1)
    own_tickets = feed(request, 2)
    tickets_responded = feed(request, 3)

    print(request.user.id)

    context = {
        "posts_followed": posts_followed,
        "own_tickets": own_tickets,
        "tickets_responded": tickets_responded,
    }

    return render(request,
                  "review/home.html",
                  context)


class CreateTicket(View):
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
            return redirect("ticket-detail", ticket.id)
        return redirect("create-ticket")


class TicketView(View):
    def get(self, request, ticket_id):
        ticket = get_object_or_404(models.Ticket, id=ticket_id)
        return render(request,
                      "review/ticket_detail.html",
                      {"ticket": ticket})


class UpdateTicket(View):
    form = forms.TicketForm

    def get(self, request, ticket_id):
        ticket = get_object_or_404(models.Ticket, id=ticket_id)
        form = self.form(instance=ticket)
        return render(request,
                      "review/update_ticket.html",
                      {"form": form})

    def post(self, request, ticket_id):
        ticket = get_object_or_404(models.Ticket, id=ticket_id)
        form = self.form(request.POST, request.FILES)
        if form.is_valid():
            ticket.title = form.cleaned_data["title"]
            ticket.description = form.cleaned_data["description"]
            ticket.image = form.cleaned_data["image"]
            ticket.save()
            return redirect("ticket-detail", ticket_id)
        return redirect("update-ticket", ticket_id)


class DeleteTicket(View):
    def get(self, request, ticket_id):
        ticket = get_object_or_404(models.Ticket, id=ticket_id)
        return render(request,
                      "review/delete_ticket.html",
                      {"ticket": ticket})

    def post(self, request, ticket_id):
        ticket = get_object_or_404(models.Ticket, id=ticket_id)
        ticket.delete()
        return redirect("home")


class CreateReview(View):
    form = forms.ReviewForm

    def get(self, request):
        form = self.form()
        return render(request,
                      "review/create_review.html",
                      {"form": form})

    def post(self, request):
        form = self.form(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.save()
            return redirect("review-detail", review.id)
        return redirect("create-review")


class CreateReviewResponse(View):
    form = forms.ReviewForm
    model = models.Ticket

    def get(self, request, ticket_id):
        form = self.form()
        ticket = self.model.objects.get(id=ticket_id)
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
            return redirect("review-detail", review.id)
        return redirect("create-review-response")


class ReviewView(View):
    def get(self, request, review_id):
        review = get_object_or_404(models.Review, id=review_id)
        return render(request,
                      "review/review_detail.html",
                      {"review": review})


class UpdateReview(View):
    form = forms.ReviewForm

    def get(self, request, review_id):
        review = get_object_or_404(models.Review, id=review_id)
        form = self.form(instance=review)
        return render(request,
                      "review/update_review.html",
                      {"form": form})

    def post(self, request, review_id):
        review = get_object_or_404(models.Review, id=review_id)
        form = self.form(request.POST)
        if form.is_valid():
            # review.ticket = form.cleaned_data["ticket"]
            review.rating = form.cleaned_data["rating"]
            review.headline = form.cleaned_data["headline"]
            review.body = form.cleaned_data["body"]
            review.save()
            return redirect("review-detail", review_id)
        return redirect("update-review", review_id)


class DeleteReview(View):
    def get(self, request, review_id):
        review = get_object_or_404(models.Review, id=review_id)
        return render(request,
                      "review/delete_review.html",
                      {"review": review})

    def post(self, request, review_id):
        review = get_object_or_404(models.Review, id=review_id)
        review.delete()
        return redirect("home")


class FollowedUsersPage(View):
    def get(self, request):
        follows = models.UserFollows.objects.all()

        return render(request,
                      "review/followed_users.html",
                      {"follows": follows})


class Follow(View):
    form = forms.UserFollowsForm

    def get(self, request):
        form = self.form()
        return render(request,
                      "review/follow.html",
                      {"form": form})

    def post(self, request):
        form = self.form(request.POST)
        if form.is_valid():
            follow = form.save(commit=False)
            follow.user = request.user
            follow.save()
            return redirect("followed-users")
        return redirect("follow")


class DeleteFollow(View):
    model = models.UserFollows

    def get(self, request, follow_id):
        follow = self.model.objects.get(id=follow_id)

        return render(request,
                      "review/delete_follow.html",
                      {"follow": follow})

    def post(self, request, follow_id):
        follow = self.model.objects.get(id=follow_id)
        follow.delete()
        return redirect("followed-users")
