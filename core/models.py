from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

# there are two ways 
# 1. Extend User Model          ------> it must be done at the START of PROJECT
# 1. Create User Profile Model  ------> it can be done at any Stage of Project


# Extend User Model
class User(AbstractUser):
    # pass  # again it must be done at the START of PROJECT
    email = models.EmailField(unique=True)
