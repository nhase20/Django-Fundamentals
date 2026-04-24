from django import forms
from .models import Client

# Which attributes the forms of each client should show from their respecive classes
class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        exclude = ['user']
        fields = '__all__'
