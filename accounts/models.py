from django.db import models
from django.utils import timezone


class UserAccount(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    username = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    avatar = models.ImageField(upload_to='media/', null=True, blank=True)
    # category = models.ForeignKey(Category, on_delete=models.DO_NOTHING)

