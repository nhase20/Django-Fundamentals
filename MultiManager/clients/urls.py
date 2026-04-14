from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('onboarding/<str:client_type>/', views.onboarding, name='onboarding'),
    path('retail-dashboard/', views.retail_dashboard, name='retail-dashboard'),
    path('institutional-dashboard/', views.institutional_dashboard, name='institutional-dashboard'),
]