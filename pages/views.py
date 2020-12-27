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
import json
import requests

@login_required
def transferView(request):
    request.session['to'] = request.GET.get('to')
    request.session['amount'] = int(request.GET.get('amount'))
    amount = request.session['amount']
    to = User.objects.get(username=request.session['to'])
    request.user.account.points -= amount
    to.account.points += amount
    request.user.account.save()
    to.account.save()

    return redirect('/')

def downloadView(request, fileid):
    f = File.objects.get(pk=fileid)
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
    if request.method == 'POST':
        request.session['username'] = request.POST.get('username')
        request.session['password1'] = request.POST.get('password1')
        hashed = make_password(request.session['password1'], salt=None, hasher='default')

        user = User.objects.create(username=request.session['username'], password=hashed)
        account = Account.objects.create(owner=user, pet=request.POST.get('pet'), petage=request.POST.get('petage'), points=request.POST.get('points'), creditcard=request.POST.get('creditcard'))
        userinfo = Userinfo.objects.create(name=request.session['username'], password=request.session['password1'], admin=0)
        return redirect('/')
    else:
        form = UserCreationForm()
    return render(request, 'pages/register.html', {'form': form})