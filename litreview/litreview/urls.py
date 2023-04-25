"""litreview URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

import authentication.views
import review.views

urlpatterns = [
    re_path(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),
    path("", authentication.views.LoginPageView.as_view()),
    path("login/", authentication.views.LoginPageView.as_view(), name="login"),
    path("signup/", authentication.views.SignupPage.as_view(), name="signup"),
    path("logout/", authentication.views.logout_user, name="logout"),
    path("feed/", review.views.Feed.as_view(), name="feed"),
    path("posts/", review.views.PostsPage.as_view(), name="posts"),
    path("ticket/create/", review.views.CreateTicket.as_view(), name="create-ticket"),
    path("ticket/<int:ticket_id>/update/", review.views.UpdateTicket.as_view(), name="update-ticket"),
    path("ticket/<int:ticket_id>/delete/", review.views.DeleteTicket.as_view(), name="delete-ticket"),
    path("review/create/", review.views.CreateReview.as_view(), name="create-review"),
    path("review/create/ticket/<int:ticket_id>/",
         review.views.CreateReviewResponse.as_view(),
         name="create-review-response"),
    path("review/<int:review_id>/update/", review.views.UpdateReview.as_view(), name="update-review"),
    path("review/<int:review_id>/delete/", review.views.DeleteReview.as_view(), name="delete-review"),
    path("follows/", review.views.FollowPage.as_view(), name="followed-users"),
    path("follow/delete/<int:follow_id>/", review.views.DeleteFollow.as_view(), name="delete-follow"),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


handler403 = "review.views.permission_denied_view"
handler404 = "review.views.page_not_found_view"
