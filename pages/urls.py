from django.urls import path
from .views import homePage, transferView, addView, downloadView, addMailView, mailView

urlpatterns = [
    path('', homePage, name='home'),
    path('accounts/profile/', homePage, name='home'),
    path('add/', addView, name='add'),
    path('download/<int:fileid>', downloadView, name='add'),
    path('transfer/', transferView, name='transfer'),
    path('addmail/', addMailView, name='add'),
    path('mail/', mailView, name='mail'),
]