from django.http import HttpRequest
from django.shortcuts import render


def home(requests):
    return render(HttpRequest, template_name='index.html')
