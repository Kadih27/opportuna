

from django.contrib import admin
from django.http.response import HttpResponse
from django.urls import path,include
from .views import *



urlpatterns = [
    path('test/', http_response),
]