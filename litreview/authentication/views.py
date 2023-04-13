from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.views import View

from . import forms


class LoginPageView(View):
    form = forms.LoginForm
    template_name = "authentication/login.html"

    def get(self, request):
        form = self.form()
        return render(request,
                      self.template_name,
                      {"form": form})

    def post(self, request):
        form = self.form()
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"],
            )
            if user is not None:
                login(request, user)
                return redirect("home")

        return render(request,
                      self.template_name,
                      {"form": form})


class RegisterPageView(View):
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
            user = form.save()
            login(request, user)
            return redirect("home")

        return render(request,
                      self.template_name,
                      {"form": form})

