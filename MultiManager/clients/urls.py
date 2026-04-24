from django.urls import path
from . import views

# Shortcut paths to different pages in the template
urlpatterns = [
    path('', views.home, name='home'), # Normal home page
    path('onboarding/', views.onboarding, name='onboarding'), # Form page for each user
    path('about/', views.about, name='about'), # About page for first time users
    path('dashboard/', views.dashboard, name='dashboard') # Retail dashboard page
]