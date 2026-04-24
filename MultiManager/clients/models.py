from django.db import models
from django.contrib.auth.models import User
from django.db import models
from .automations import retail_benchmark_selector,retail_asset_allocation

# Retail Client data
class Client(models.Model):

        # How much risk the business is willing to take
    RISK_PROFILE = [
        ('conservative','Conservative'),
        ('aggressive','Aggressive'), 
        ('moderate','Moderate'),
        ('mod-aggressive','Moderate Aggressive')
    ]

    # How fast they want their funds
    RISK_TOLERANCE = [
        ('money maket','Money Market'),
        ('sa ma income','(ASISA) South African MA Income'), 
        ('sa ma low equity','(ASISA) South African MA Low Equity'),
        ('sa ma medium equity','(ASISA) South African MA Medium Equity'),
        ('sa ma high equity','(ASISA) South African MA High Equity'),
        ('ww ma flexible','(ASISA) Worldwide MA Flexible'),
        ('sa equity','SA Equity'),
        ('usd cash','USD Cash'),
        ('eaa fund usd cautious','EAA Fund USD Cautious Allocation'),
        ('eaa fund usd moderate','EAA Fund USD Moderate Allocation'),
        ('eaa fund usd aggressive','EAA Fund USD Aggressive Allocation'),
        ('international equity','International Equity (ZAR)'),
    ]

    RISK_RATING = [
        ('low', 'Low'),
        ('pure equity', 'Pure Equity'),
        ("low-medium", 'Low-Medium'),
        ('medium', 'Medium'),
        ("high", 'High'),
        ('flexible','Flexible'),
    ]

    # user instance which has a one-to-one reltionship with profile 
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    # A few details that can be used to create a suggestion to the user and create a custom dashboard
    name = models.CharField(max_length=100,default="user")
    risk_rating = models.CharField(choices=RISK_RATING)
    age = models.PositiveIntegerField(default=18)
    risk_tolerance = models.CharField(choices= RISK_TOLERANCE)
    investment_goal = models.CharField(max_length=100,default="None")
    time_horizon = models.PositiveBigIntegerField()
    risk_profile = models.CharField(choices=RISK_PROFILE)
    
    @property
    def benchmark(self):
        return retail_benchmark_selector(self)
    @property
    def asset_allocation(self):
        return retail_asset_allocation(self)

    def __str__(self):
        return self.name



# Client Profile information
class Profile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # link to your existing models
    client = models.OneToOneField(Client,null=True,blank=True,on_delete=models.CASCADE)

# Client portfolio
class Portfolio(models.Model):
    
    name = models.CharField(max_length=100,default="user")
    client = models.OneToOneField(Client,null=True,blank=True,on_delete=models.CASCADE)
    total_value = models.FloatField(null=True,blank=True,default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    # custom method to create one portfolio for each client
    @staticmethod
    def create_portfolio(client):
        portfolio = Portfolio.objects.create(
            client=client if hasattr(client, 'Client') else None,
            total_value=0
        )
        return portfolio

# Asset data, different types of assets
class AssetManaged(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    asset_type = models.CharField(max_length=50)  
    name = models.CharField(max_length=100)  
    value = models.FloatField()
    allocation_percentage = models.FloatField()

