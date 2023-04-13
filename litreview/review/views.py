from django.shortcuts import render, redirect
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


class TicketView(View):
    form = forms.TicketForm

    def get(self, request):
        form = self.form()
        return render(request,
                      "review/ticket_detail.html",
                      {"form": form})


class CreateTicket(View):
    pass


class UpdateTicket(View):
    pass


class ReviewView(View):
    form = forms.ReviewForm

    def get(self, request):
        form = self.form()
        return render(request,
                      "review/review_detail.html",
                      {"form": form})

