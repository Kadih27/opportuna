from django.contrib import admin
from django.http.response import HttpResponse
from django.urls import path,include
from apps.account import views



urlpatterns = [
    path("register_student/", views.register_student, name="register_student"),
    path("register_company/", views.register_company, name="register_company"),
    path(
        "register/account-activation/<uidb64>/<token>",
        views.activate,
        name="activate",
    ),
    path('login_view/', views.login_view, name='login_view'),
    path('logout/', views.logout_view, name='logout'),
]