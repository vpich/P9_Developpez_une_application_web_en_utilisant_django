from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views import View
from django.utils.decorators import method_decorator
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView

from . import forms, models

# class Feed(View):
#     pass


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
    return render(request,
                  "review/home.html")


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


class ReviewView(View):
    form = forms.ReviewForm

    def get(self, request):
        form = self.form()
        return render(request,
                      "review/review_detail.html",
                      {"form": form})

