from django import forms
from .models import Client

# Which attributes the forms of each client should show from their respecive classes
class ClientQuestionnaireForm(forms.Form):
    name = forms.CharField(label="Client's full name")
    age  = forms.IntegerField(label="Client's age", min_value=18)

    PURPOSE_CHOICES = [
        ('retirement', 'Retirement planning'),
        ('education',  'Education or a specific goal'),
        ('wealth',     'Long-term wealth building'),
    ]
    purpose = forms.ChoiceField(
        label="What is this money for?",
        choices=PURPOSE_CHOICES
    )

    HORIZON_CHOICES = [
        ('short',  'Less than 5 years'),
        ('medium', '5–10 years'),
        ('long',   'More than 10 years'),
    ]
    time_horizon = forms.ChoiceField(
        label="How long will it be invested?",
        choices=HORIZON_CHOICES
    )

    emergency_fund = forms.ChoiceField(
        label="Does the client have 3–6 months of emergency savings?",
        choices=[('yes', 'Yes'), ('no', 'No')]
    )

    VOLATILITY_CHOICES = [
        ('low',    'Uncomfortable — I want stability'),
        ('medium', 'Neutral — some ups and downs are fine'),
        ('high',   'Comfortable — I focus on long-term growth'),
    ]
    volatility_comfort = forms.ChoiceField(
        label="How do you feel about investment ups and downs?",
        choices=VOLATILITY_CHOICES
    )

    INCOME_CHOICES = [
        ('income',   'I need regular income'),
        ('balanced', 'A mix of both'),
        ('growth',   'I want maximum growth'),
    ]
    income_or_growth = forms.ChoiceField(
        label="Do you need income or growth?",
        choices=INCOME_CHOICES
    )
