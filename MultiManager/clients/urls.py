# clients/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('',                              views.home,              name='home'),
    path('logout/',                       views.logout_view,       name='logout'),
    path('register/advisor/',             views.register_advisor,  name='register_advisor'),
    path('about/',                        views.about,             name='about'),
    path('dashboard/',                    views.dashboard,         name='dashboard'),
    path('advisor/dashboard/',            views.advisor_dashboard, name='advisor_dashboard'),
    path('overview/',                     views.admin_overview,    name='admin_overview'),
    path('create-client/',                views.create_client,     name='create_client'),
    path('client/<int:client_id>/',           views.client_detail,     name='client_detail'),
    path('client/<int:client_id>/edit/',      views.edit_client,       name='edit_client'),
    path('client/<int:client_id>/portfolio/', views.add_portfolio,     name='add_portfolio'),
    path('results/<int:client_id>/',      views.portfolio_results, name='portfolio_results'),
    path('advisor/portfolios/', views.portfolio_list, name='portfolio_list'),
]