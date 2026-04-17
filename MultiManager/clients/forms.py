from django import forms
from .models import RetailClient,InstitutionalClient

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
