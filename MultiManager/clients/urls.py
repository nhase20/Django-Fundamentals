# clients/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('',              views.home,           name='home'),
    path('onboarding/',   views.onboarding,     name='onboarding'),
    path('about/',        views.about,          name='about'),
    path('dashboard/',    views.dashboard,       name='dashboard'),
    path('overview/',     views.admin_overview,  name='admin_overview'),  # ADD THIS
]