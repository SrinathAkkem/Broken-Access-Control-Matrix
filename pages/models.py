from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
# Create your models here.

class Account(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    pet = models.CharField(max_length=200)
    petage = models.IntegerField()
    points = models.IntegerField(default=0)
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

class Message(models.Model):
	source = models.ForeignKey(User, on_delete=models.CASCADE, related_name='source')
	target = models.ForeignKey(User, on_delete=models.CASCADE, related_name='target')
	content = models.TextField()
