from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views import View
from django.utils.decorators import method_decorator

from authentication.views import logout_user


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

