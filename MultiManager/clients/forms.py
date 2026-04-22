from django import forms
from .models import RetailClient,InstitutionalClient

# Which attributes the forms of each client should show from their respecive classes
class RetailClientForm(forms.ModelForm):
    class Meta:
        model = RetailClient
        exclude = ['user']
        fields = '__all__'

class InstitutionalClientForm(forms.ModelForm):
    class Meta:
        model = InstitutionalClient
        exclude = ['user']
        fields = '__all__'
