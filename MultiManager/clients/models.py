from django.db import models
from .automations import classify_retailer, classify_institution, retail_benchmark_selector, select_institutional_benchmark,institutional_asset_allocation,retail_asset_allocation

class RetailClient(models.Model):
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

    name = models.CharField(max_length=100,default="user")
    email = models.EmailField()
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


class InstitutionalClient(models.Model):

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

    # BENCHMARK = [
    #     ('s&p 500','S&P 500'),
    #     ('bond index','Bond index'),
    #     ('multi-asset','Multi-asset benchmark'),
    #     ('custom','Custom'),
    # ]

    # The portfolio's performance relative to the benchmark
    PERFORMANCE_REL_BENCHMARK = [
        ('match','Match benchmark'),
        ('outperforn','Outperform'), 
        ('minimize','Minimize downside vs benchmark'),
    ]

    RISK_TOLERANCE = [
        ('conservative','Conservative'),
        ('aggressive','Aggressive'), 
        ('moderate','Moderate'),
    ]
    LIQUIDITY_REQUIREMENTS = [
        ('high','Daily'),
        ('medium','Monthly'), 
        ('low','long-term'),
    ]
    ESG_POLICY = [
        ('yes','Yes'),
        ('partial','No'), 
        ('no','Partial'),
    ]

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

class Portfolio(models.Model):
    
    retail_client = models.OneToOneField(RetailClient,null=True,blank=True,on_delete=models.CASCADE)
    institutional_client = models.OneToOneField(InstitutionalClient,null=True,blank=True,on_delete=models.CASCADE)
    total_value = models.FloatField(null=True,blank=True,default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def create_portfolio(client):
        portfolio = Portfolio.objects.create(
            retail_client=client if hasattr(client, 'retailclient') else None,
            institutional_client=client if hasattr(client, 'institutionalclient') else None,
            total_value=0
        )
        return portfolio

class AssetManaged(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    asset_type = models.CharField(max_length=50)  
    name = models.CharField(max_length=100)  
    value = models.FloatField()
    allocation_percentage = models.FloatField()

