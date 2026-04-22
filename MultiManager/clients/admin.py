from django.contrib import admin
from .models import RetailClient,InstitutionalClient,Portfolio,AssetManaged,Profile

# Data tabs to be open on the admin UI
admin.site.register(RetailClient)
admin.site.register(InstitutionalClient)
admin.site.register(Portfolio)
admin.site.register(AssetManaged)
admin.site.register(Profile)