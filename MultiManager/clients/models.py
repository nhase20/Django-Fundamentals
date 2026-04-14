from django.db import models

class RetailClient(models.Model):
    INVESTMENT_GOALS = [
        ('retirement', 'Retirement Planning'),
        ('independence', 'Financial Independence'),
        ('preservation', 'Wealth Preservation'),
    ]

    name = models.CharField(max_length=100)
    email = models.EmailField()
    client_goals = models.CharField(max_length=20, choices=INVESTMENT_GOALS)
    age = models.PositiveIntegerField(max_length=3)
    risk_tolerance = models.CharField(max_length=50)
    investment_goal = models.CharField(max_length=100)
    time_horizon = models.IntegerField()
    identity_number = models.PositiveBigIntegerField(max_length=13)

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

    BENCHMARK = [
        ('s&p 500','S&P 500'),
        ('bond index','Bond index'),
        ('multi-asset','Multi-asset benchmark'),
        ('custom','Custom'),
    ]

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
    organization_type = models.CharField(max_length=20, choices=ORGANIZATION_TYPE)
    assets_held = models.PositiveBigIntegerField()
    # Aims and objectives
    target_return = models.PositiveSmallIntegerField(max_length=3,default=0)
    return_objective = models.CharField(max_length=20, choices=RETURN_OBJECTIVE)
    benchmark =  models.CharField(max_length=20, choices= BENCHMARK)
    performance = models.CharField(max_length=20, choices= PERFORMANCE_REL_BENCHMARK)
    risk_tolerance = models.CharField(max_length=20, choices= RISK_TOLERANCE)
    liquidity = models.CharField(max_length=20, choices= LIQUIDITY_REQUIREMENTS)
    manager_numbers = models.PositiveIntegerField(max_length=3)
    time_horizon = models.IntegerField()
    
    def __str__(self):
        return self.name