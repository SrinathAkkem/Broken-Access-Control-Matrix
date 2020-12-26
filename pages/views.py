from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import Account
from django.contrib.auth.models import User
from .models import File, Message, Mail
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
import json
import requests

@login_required
def transferView(request):
    request.session['to'] = request.GET.get('to')
    request.session['amount'] = int(request.GET.get('amount'))
    amount = request.session['amount']
    to = User.objects.get(username=request.session['to'])
    request.user.account.balance -= amount
    to.account.balance += amount
    request.user.account.save()
    to.account.save()

    return redirect('/')

def deleteView(request):
    f = File.objects.get(pk=request.POST.get('id'))
    f.delete()
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

@csrf_exempt 
def mailView(request):
	Mail.objects.create(content=request.body.decode('utf-8'))
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

# Create your views here.