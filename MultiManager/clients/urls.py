from django.urls import path
from . import views

# Shortcut paths to different pages in the template
urlpatterns = [
    path('', views.home, name='home'), # Normal home page
    path('onboarding/<str:client_type>/', views.onboarding, name='onboarding'), # Form page for each user
    path('about/', views.about, name='about'), # About page for first time users
    path('institutional-dashboard/', views.institutional_dashboard, name='institutional-dashboard'), # Institutional dashbooard page
    path('retail-dashboard/', views.retail_dashboard, name='retail-dashboard') # Retail dashboard page
]