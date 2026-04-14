from django.contrib import admin
from .models import RetailClient,InstitutionalClient

admin.site.register(RetailClient)
admin.site.register(InstitutionalClient)