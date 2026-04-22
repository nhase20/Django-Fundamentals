from django.db import models
from django.contrib.auth.models import User
from django.db import models
from .automations import classify_retailer, classify_institution, retail_benchmark_selector, select_institutional_benchmark,institutional_asset_allocation,retail_asset_allocation

# Retail Client data
class RetailClient(models.Model):

    # What the user hopes to achieve at the end of this
    INVESTMENT_GOALS = [
        ('retirement', 'Retirement Planning'),
        ('independence', 'Financial Independence'),
        ('preservation', 'Wealth Preservation'),
    ]

    RISK_TOLERANCE = [
        (1, 'Poor'),
        (2, 'Fair'),
        (3, 'Good'),
        (4, 'Very Good'),
        (5, 'Excellent'),
    ]

    # user instance which has a one-to-one reltionship with profile 
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)

    # A few details that can be used to create a suggestion to the user and create a custom dashboard
    name = models.CharField(max_length=100,default="user")
    client_goals = models.CharField(max_length=20, choices=INVESTMENT_GOALS)
    age = models.PositiveIntegerField()
    risk_tolerance = models.IntegerField( choices= RISK_TOLERANCE)
    investment_goal = models.CharField(max_length=100)
    time_horizon = models.PositiveBigIntegerField()
    identity_number = models.PositiveBigIntegerField()

    @property
    def risk_profile(self):
        return classify_retailer(self)
    
    @property
    def benchmark(self):
        return retail_benchmark_selector(self)
    @property
    def asset_allocation(self):
        return retail_asset_allocation(self)

    def __str__(self):
        return self.name

# Institution Client data
class InstitutionalClient(models.Model):
    # Just for details
    ORGANIZATION_TYPE = [
        ('mutual funds', 'Mutual Funds'),
        ('closed-end funds', 'Closed-end Funds'),
        ('investment trust', 'Investment Trust'),
    ]
    # The primary return objective
    RETURN_OBJECTIVE = [
        ('capital ', 'Capital Growth'),
        ('income ','Income Generation'),
        ('total ','Total Return'),
    ]

    # The portfolio's performance relative to the benchmark
    PERFORMANCE_REL_BENCHMARK = [
        ('match','Match benchmark'),
        ('outperform','Outperform'), 
        ('minimize','Minimize downside vs benchmark'),
    ]
    # How much risk the business is willing to take
    RISK_TOLERANCE = [
        ('conservative','Conservative'),
        ('aggressive','Aggressive'), 
        ('moderate','Moderate'),
    ]
    # How fast they want their funds
    LIQUIDITY_REQUIREMENTS = [
        ('high','Daily'),
        ('medium','Monthly'), 
        ('low','long-term'),
    ]
    
    ESG_POLICY = [
        ('yes','Yes'),
        ('partial','Partial'), 
        ('no','No'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)

    # About company
    organization_name = models.CharField(max_length=100, default="org")
    organization_type = models.CharField(max_length=20, choices=ORGANIZATION_TYPE)
    assets_held = models.PositiveBigIntegerField()
    # Aims and objectives
    target_return = models.PositiveSmallIntegerField()
    return_objective = models.CharField(max_length=20, choices=RETURN_OBJECTIVE)
    #benchmark =  models.CharField(max_length=20, choices= BENCHMARK)
    performance = models.CharField(max_length=20, choices= PERFORMANCE_REL_BENCHMARK)
    risk_tolerance = models.CharField(max_length=20, choices= RISK_TOLERANCE)
    liquidity = models.CharField(max_length=20, choices= LIQUIDITY_REQUIREMENTS)
    manager_numbers = models.PositiveIntegerField()
    time_horizon = models.IntegerField()

    @property
    def tier(self):
        return classify_institution(self)

    @property
    def benchmark(self):
        return select_institutional_benchmark(self)
    
    @property
    def asset_allocation(self):
        return institutional_asset_allocation(self)
    
    def __str__(self):
        return self.organization_name

# Client Profile information
class Profile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # link to your existing models
    retail_client = models.OneToOneField(RetailClient,null=True,blank=True,on_delete=models.CASCADE)
    institutional_client = models.OneToOneField(InstitutionalClient,null=True,blank=True,on_delete=models.CASCADE)

# Client portfolio
class Portfolio(models.Model):
    

    retail_client = models.OneToOneField(RetailClient,null=True,blank=True,on_delete=models.CASCADE)
    institutional_client = models.OneToOneField(InstitutionalClient,null=True,blank=True,on_delete=models.CASCADE)
    total_value = models.FloatField(null=True,blank=True,default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    # custom method to create one portfolio for each client
    @staticmethod
    def create_portfolio(client):
        portfolio = Portfolio.objects.create(
            retail_client=client if hasattr(client, 'retailclient') else None,
            institutional_client=client if hasattr(client, 'institutionalclient') else None,
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

