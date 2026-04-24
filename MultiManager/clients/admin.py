from django.contrib import admin
from .models import Client,Portfolio,AssetManaged,Profile

# Data tabs to be open on the admin UI
admin.site.register(Client)
admin.site.register(Portfolio)
admin.site.register(AssetManaged)
admin.site.register(Profile)