from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.views import View

from . import forms


class LoginPageView(View):

    def get(self, request):
        form = forms.LoginForm()
        return render(request,
                      "authentication/login.html",
                      {"form": form})

    def post(self, request):
        form = forms.LoginForm(request.POST)
        if form.password == form.password_check:
            if form.is_valid():
                user = authenticate(
                    username=form.cleaned_data["username"],
                    password=form.cleaned_data["password"],
                )
                if user is not None:
                    login(request, user)
                    return redirect("home")

        return render(request,
                      "authentication/login.html",
                      {"form": form})
