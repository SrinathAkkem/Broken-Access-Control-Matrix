from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
# Create your models here.

class Account(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    iban = models.IntegerField()
    creditcard = models.IntegerField()

def user_directory_path(instance, filename):
    return 'user_{0}/{1}'.format(instance.owner.id, filename)

class File(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    data = models.FileField(upload_to=user_directory_path)

class Userinfo(models.Model):
    name = models.CharField(max_length=200)
    password = models.CharField(max_length=200)
    admin = models.IntegerField()

class Mail(models.Model):
	content = models.TextField()

class Message(models.Model):
	source = models.ForeignKey(User, on_delete=models.CASCADE, related_name='source')
	target = models.ForeignKey(User, on_delete=models.CASCADE, related_name='target')
	content = models.TextField()
	time = models.DateTimeField(auto_now_add=True)