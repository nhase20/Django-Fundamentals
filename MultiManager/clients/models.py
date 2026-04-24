from django.db import models
from django.contrib.auth.models import User
from django.db import models
from .automations import retail_benchmark_selector,retail_asset_allocation

# Retail Client data
class Client(models.Model):

        # How much risk the business is willing to take
    # AFTER — stored values now exactly match Portfolio.risk_profile values from CSV
    RISK_PROFILE = [
        ('Conservative', 'Conservative'),
        ('Aggressive', 'Aggressive'),
        ('Moderate', 'Moderate'),
        ('Moderate Aggressive', 'Moderate Aggressive'),
        ('Global Moderate', 'Global Moderate'),
        ('Global Moderate Aggressive', 'Global Moderate Aggressive'),
        ('Global Aggressive', 'Global Aggressive'),
        ('Global Cautious', 'Global Cautious'),
        ('Global Conservative', 'Global Conservative'),
        ('Cautious', 'Cautious'),
    ]

    # AFTER — stored values match Portfolio.fund_category values from CSV exactly
    RISK_TOLERANCE = [
        ('(ASISA) South African MA Income', '(ASISA) South African MA Income'),
        ('(ASISA) South African MA Low Equity', '(ASISA) South African MA Low Equity'),
        ('(ASISA) South African MA Medium Equity', '(ASISA) South African MA Medium Equity'),
        ('(ASISA) South African MA High Equity', '(ASISA) South African MA High Equity'),
        ('(ASISA) Wwide MA Flexible', '(ASISA) Wwide MA Flexible'),  # note: CSV spells it "Wwide"
        ('EAA Fund USD Cautious Allocation', 'EAA Fund USD Cautious Allocation'),
        ('EAA Fund USD Moderate Allocation', 'EAA Fund USD Moderate Allocation'),
        ('EAA Fund USD Aggressive Allocation', 'EAA Fund USD Aggressive Allocation'),
        ('EAA Fund USD Diversified Bond - Short Term', 'EAA Fund USD Diversified Bond - Short Term'),
        ('SA Equity', 'SA Equity'),  # CSV has a trailing space — strip it in import_portfolios
    ]

    RISK_RATING = [
        ('low', 'Low'),
        ('pure equity', 'Pure Equity'),
        ("low-medium", 'Low-Medium'),
        ('medium', 'Medium'),
        ("high", 'High'),
        ('flexible','Flexible'),
    ]

    # AFTER — every stored value matches Client_Grouping in the CSV exactly
    CLIENT_GROUP = [
        ('ACS','ACS'),
        ('BKA Wealth','BKA Wealth'),
        ('Clamart Wealth','Clamart Wealth'),
        ('Delta','Delta'),
        ('Fiducia Wealth (Pty) Ltd','Fiducia Wealth (Pty) Ltd'),
        ('Fiscal Tree', 'Fiscal Tree'),
        ('Graviton', 'Graviton'),
        ('Graviton Absolute Funds','Graviton Absolute Funds'),
        ('Graviton Global Funds','Graviton Global Funds'),
        ('Graviton Hedge Funds','Graviton Hedge Funds'),
        ('Graviton Hybrid Funds', 'Graviton Hybrid Funds'),
        ('Graviton Offshore (Franchises)', 'Graviton Offshore (Franchises)'),
        ('Graviton Retirement Solution', 'Graviton Retirement Solution'),
        ('Graviton Shariah Funds','Graviton Shariah Funds'),
        ('Graviton Wealth','Graviton Wealth'),
        ('Graviton Wealth (Franchises)', 'Graviton Wealth (Franchises)'),
        ('Graviton Wealth Management','Graviton Wealth Management'),
        ('Guardian','Guardian'),
        ('Henceforward','Henceforward'),
        ('Innovate Solutions Group (Pty) Ltd','Innovate Solutions Group (Pty) Ltd'),
        ('Jurien Jordaan','Jurien Jordaan'),
        ('Justin Frittelli','Justin Frittelli'),
        ('LW Funds','LW Funds'),
        ('Latitude Wealth','Latitude Wealth'),
        ('Luthuli Capital','Luthuli Capital'),
        ('Lynnwood Financial Services (Pty) Ltd','Lynnwood Financial Services (Pty) Ltd'),
        ('NLD','NLD'),
        ('Optimate','Optimate'),
        ('PSG Wealth Bryanston','PSG Wealth Bryanston'),
        ('Rebalance', 'Rebalance'),
        ('Sanlam Multi Manager International','Sanlam Multi Manager International'),
        ('Victory House','Victory House'),
        ('Wealth Design','Wealth Design'),
        ('Zingitwa Wealth','Zingitwa Wealth'),
        ('Other','Other'),
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
    client_group = models.CharField(choices=CLIENT_GROUP,default="other")
    # @property
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

    client_group = models.CharField(max_length=100,default="Other")
    name = models.CharField(max_length=100,default="user")
    client = models.OneToOneField(Client,null=True,blank=True,on_delete=models.CASCADE)
    total_value = models.FloatField(null=True,blank=True,default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    risk_profile =  models.CharField(max_length=100,default="none")
    fund_category =  models.CharField(max_length=100,default="none")

    # custom method to create one portfolio for each client
    @staticmethod
    def portfolioName(client):
        return Portfolio.objects.filter(
            client_group__iexact=client.client_group,
            risk_profile__iexact=client.risk_profile,
            fund_category__iexact=client.risk_tolerance
        )
    
    def __str__(self):
        return f"{self.name}'s portfolio"

# Asset data, different types of assets
class AssetManaged(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    asset_type = models.CharField(max_length=50)  
    name = models.CharField(max_length=100)  
    value = models.FloatField()
    allocation_percentage = models.FloatField()

