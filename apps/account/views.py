from django.http.response import HttpResponse
from django.shortcuts import render

# Create your views here.

def http_response(request):
    return render(request, "apps/account/test.html")
