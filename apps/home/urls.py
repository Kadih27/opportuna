from django.urls import path
from apps.home import views



urlpatterns = [
    path("", views.index, name="index"),
    path("home/", views.index, name="default_home"),
    path("404/", views.error_404, name="404"),
    path('contactus',views.contact,name='contact'),
    path('search', views.search_results_seeker, name='search_results_seeker'),
]