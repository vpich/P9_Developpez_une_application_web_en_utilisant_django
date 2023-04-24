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
            return redirect("feed")
        return render(request,
                      self.template_name,
                      {"form": form})

    def post(self, request):
        form = self.form(request.POST)
        message = "Saisie incorrecte."
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"],
            )
            if user is not None:
                message = f"Bienvenue {user.username} !"
                login(request, user)
                messages.add_message(request, messages.SUCCESS, message)
                return redirect("feed")
            elif self.users.filter(username=form.cleaned_data["username"]):
                message = "Le mot de passe est erroné."
            elif user is None:
                message = "L'utilisateur n'existe pas. Veuillez créer un compte si vous n'en possédez pas."
            else:
                message = "Le nom d'utilisateur ou le mot de passe est erroné."
        messages.add_message(request, messages.ERROR, message)

        return render(request,
                      self.template_name,
                      {"form": form})


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
            message = f"Votre compte a été créé. Bienvenue {user.username} !"
            messages.add_message(request, messages.SUCCESS, message)
            return redirect("feed")
        message = "Le nom d'utilisateur ou le mot de passe est invalide."
        messages.add_message(request, messages.ERROR, message)

        return render(request,
                      self.template_name,
                      {"form": form})


def logout_user(request):
    logout(request)
    return redirect("login")
