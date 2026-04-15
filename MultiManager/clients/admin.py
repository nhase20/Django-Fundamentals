from django.contrib import admin
from .models import RetailClient,InstitutionalClient,Portfolio

admin.site.register(RetailClient)
admin.site.register(InstitutionalClient)
admin.site.register(Portfolio)