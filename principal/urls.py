from django import views
from django.urls import path
#from django.views.generic import TemplateView
from . import views


urlpatterns = [
    path('', views.home, name='home'),
]
