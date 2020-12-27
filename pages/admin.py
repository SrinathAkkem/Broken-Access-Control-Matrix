from django.contrib import admin


from .models import Account, File, Message, Userinfo

admin.site.register(Account)

admin.site.register(File)

admin.site.register(Message)

admin.site.register(Userinfo)
# Register your models here.
