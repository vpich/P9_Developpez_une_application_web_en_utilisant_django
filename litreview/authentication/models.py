from django.db import models
from django.contrib.auth.models import AbstractBaseUser, UserManager


class User(AbstractBaseUser):
    username = models.CharField(max_length=150, unique=True)
    objects = UserManager()

    USERNAME_FIELD = 'username'
