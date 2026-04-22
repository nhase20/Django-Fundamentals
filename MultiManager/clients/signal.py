from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import  Portfolio, Profile

# Setting a trigger for actions that must take place when user is created
@receiver(post_save, sender=User)
def create_portfolio(sender, instance, created, **kwargs):
    if created:

        # Portfolio.create_portfolio(instance)
        Profile.objects.get_or_create(user=instance)# Auto create a profile whenever user gets created