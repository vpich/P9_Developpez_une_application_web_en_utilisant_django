from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.views import View
from django.contrib import messages

from . import forms, models


class LoginPageView(View):
    form = forms.LoginForm
    template_name = "authentication/login.html"
    users = models.User.objects.all()

    def get(self, request):
        form = self.form()
        if request.user in self.users:
            return redirect("home")
        return render(request,
                      self.template_name,
                      {"form": form})

    def post(self, request):
        form = self.form(request.POST)
        message = "??"
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"],
            )
            message = "L'utilisateur n'existe pas"
            if user is not None:
                message = "Vous êtes bien connecté"
                login(request, user)
                messages.add_message(request, messages.SUCCESS, message)
                return redirect("home")

        return render(request,
                      self.template_name,
                      {"form": form,
                       "message": message})


class SignupPage(View):
    form = forms.SignupForm
    template_name = "authentication/signup.html"

    def get(self, request):
        form = self.form()
        return render(request,
                      self.template_name,
                      {"form": form})

    def post(self, request):
        form = self.form(request.POST)
        if form.is_valid():
            user = form.save(self)
            login(request, user)
            message = "Votre compte a été créé"
            messages.add_message(request, messages.SUCCESS, message)
            return redirect("home")

        return render(request,
                      self.template_name,
                      {"form": form})


def logout_user(request):
    logout(request)
    return redirect("login")
