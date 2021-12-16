from django.shortcuts import render

from django.http import HttpResponse
from .models import Ui

# Create your views here.

def index(request):
    list_created = 'Список созданных сотрудников\n'
    for man in Ui.objects.order_by('name'):
        list_created += man.name + ' ' + str(man.date) + '\n'


    return HttpResponse(list_created, content_type='text/plain; charset=utf-8')
