from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import Account, Userinfo
from django.contrib.auth.models import User
from .models import File, Message
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.hashers import make_password
from django.contrib import messages
import json
import requests
import sys
import sqlite3
import string
import os
import requests

def login(request):

    if request.method == 'GET':
        content = ''
        return render(request, 'templates/pages/login.html', {'context': context})

    elif request.method == 'POST':
        username == request.POST.get('username')
        password == request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

        else:
            context = {'error': 'Wrong credentials'}
            return render(request, 'templates/pages/login.html', {'context': context})

def downloadView(request, fileid):
    f = File.objects.get(pk=fileid)
    # if f.owner != request.user:
    #   return redirect('/')
   
    filename = f.data.name.split('/')[-1]
    response = HttpResponse(f.data, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=%s' % filename

    return response

def addView(request):
	data = request.FILES.get('file')
	f = File(owner=request.user, data=data)
	f.save()
	return redirect('/')

def deleteView(request):
    f = File.objects.get(pk=request.POST.get('id'))
    f.delete()
    return redirect('/')

@csrf_exempt 
def mailView(request):
	print(request.body.decode('utf-8'))
	return HttpResponse('')
	

@login_required
def addMailView(request):
	target = User.objects.get(username=request.POST.get('to'))
	Message.objects.create(source=request.user, target=target, content=request.POST.get('content'))
	return redirect('/')


@login_required
def homePage(request):
    messages = Message.objects.filter(Q(source=request.user.id) | Q(target=request.user.id))
    accounts = Account.objects.exclude(owner_id=request.user.id)
    files = File.objects.filter(owner=request.user)
    usr = User.objects.get(Q(username=request.user))
    uploads = [{'id': f.id, 'name': f.data.name.split('/')[-1]} for f in files]
    users = User.objects.exclude(pk=request.user.id)

    return render(request, 'pages/index.html', {'accounts':accounts, 'uploads' : uploads, 'msgs': messages, 'users': users})


def register(request):

    DEFAULT_PATH = os.path.join(os.path.dirname(__file__), '../db.sqlite3')
    # form = UserCreationForm(request.POST)

    if request.method == 'POST':

        usrn = request.POST.get('username')
        pw1 = request.POST.get('password1')
        pw2 = request.POST.get('password2')

        conn = sqlite3.connect(DEFAULT_PATH)
        cursor = conn.cursor()

        query = "SELECT username FROM auth_user WHERE username='%s'" % (usrn)
        # query = User.objects.filter(username=usrn).exists()

        response = cursor.execute(query).fetchall()
        # response = cursor.execute("SELECT username FROM auth_user WHERE username=?", (usrn,)).fetchall()
       
        if response != [] or pw1 != pw2:
            for row in response:
                messages.error(request, 'username' + str(row) + ' already in use!')
            return redirect('/register')

      # if form.is_valid():
      #     form.save()
      #     hashed = make_password(pw1, salt=None, hasher='default')
      #     user = User.objects.create(username=usrn, password=hashed)
      #     user = authenticate(username=usrn, password=pw1)
      #       if User is not None:
      #               account = Account.objects.create(owner=user, iban=request.POST.get('iban'), creditcard=request.POST.get('creditcard'))
      #               userinfo = Userinfo.objects.create(name=usrn, password=pw1, admin=0)
      #               return redirect('/')
      #      else: 
      #           form = UserCreationForm()
#   return render (request, 'pages/register.html, {'form': form })

        else:
            hashed = make_password(pw1, salt=None, hasher='default')
            user = User.objects.create(username=usrn, password=hashed)
            account = Account.objects.create(owner=user, iban=request.POST.get('iban'), creditcard=request.POST.get('creditcard'))
            userinfo = Userinfo.objects.create(name=usrn, password=pw1, admin=0)
            return redirect('/')
    else:
        form = UserCreationForm()
    return render(request, 'pages/register.html', {'form': form})