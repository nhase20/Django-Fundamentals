from django.db import models

class Client(models.Model):
    CLIENT_TYPE_CHOICES = [
        ('retail', 'Retail'),
        ('institutional', 'Institutional'),
    ]

    name = models.CharField(max_length=100)
    email = models.EmailField()
    client_type = models.CharField(max_length=20, choices=CLIENT_TYPE_CHOICES)

    risk_tolerance = models.CharField(max_length=50)
    investment_goal = models.CharField(max_length=100)
    time_horizon = models.IntegerField()

    def __str__(self):
        return self.name