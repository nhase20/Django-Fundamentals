from django import forms
from .models import RetailClient,InstitutionalClient

class RetailClientForm(forms.ModelForm):
    class Meta:
        model = RetailClient
        fields = '__all__'

class InstitutionalClientForm(forms.ModelForm):
    class Meta:
        model = InstitutionalClient
        fields = '__all__'
