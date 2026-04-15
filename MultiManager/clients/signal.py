from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import RetailClient, Portfolio

@receiver(post_save, sender=RetailClient)
def create_portfolio(sender, instance, created, **kwargs):
    if created:
        Portfolio.create_portfolio(instance)