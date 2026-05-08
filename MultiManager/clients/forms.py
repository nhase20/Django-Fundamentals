from django import forms

class ClientQuestionnaireForm(forms.Form):

    # ── Step 1: Identity ─────────────────────────────────────────────────
    name = forms.CharField(label="Client's full name")
    age  = forms.IntegerField(label="Client's age", min_value=18)

    # ── Step 2: Purpose & Horizon (grouped — both are "where are we going") ──
    PURPOSE_CHOICES = [
        ('retirement', 'Retirement planning'),
        ('education',  'Education or a specific goal'),
        ('wealth',     'Long-term wealth building'),
    ]
    purpose = forms.ChoiceField(label="What is this money for?", choices=PURPOSE_CHOICES)

    HORIZON_CHOICES = [
        ('short',  'Less than 5 years'),
        ('medium', '5–10 years'),
        ('long',   'More than 10 years'),
    ]
    time_horizon = forms.ChoiceField(label="How long will it be invested?", choices=HORIZON_CHOICES)

    # ── Step 3: Risk attitude (grouped — both are about comfort with risk) ──
    VOLATILITY_CHOICES = [
        ('low',    'Uncomfortable — I want stability'),
        ('medium', 'Neutral — some ups and downs are fine'),
        ('high',   'Comfortable — I focus on long-term growth'),
    ]
    volatility_comfort = forms.ChoiceField(
        label="How does the client feel about investment ups and downs?",
        choices=VOLATILITY_CHOICES
    )

    INCOME_CHOICES = [
        ('income',   'Regular income'),
        ('balanced', 'A mix of both'),
        ('growth',   'Maximum growth'),
    ]
    income_or_growth = forms.ChoiceField(
        label="Does the client need income from this investment, or growth?",
        choices=INCOME_CHOICES
    )

    # ── Step 4: Knowledge & Capacity (grouped — both assess readiness) ───
    KNOWLEDGE_CHOICES = [
        ('none',    'No investment knowledge'),
        ('limited', 'Limited — knows the basics'),
        ('fair',    'Fair / reasonable understanding'),
        ('above',   'Above average'),
        ('expert',  'Expert'),
    ]
    investment_knowledge = forms.ChoiceField(
        label="How would you rate the client's investment knowledge?",
        choices=KNOWLEDGE_CHOICES
    )

    has_income = forms.ChoiceField(
        label="Does the client have a regular source of income?",
        choices=[('yes', 'Yes'), ('no', 'No')]
    )

    emergency_fund = forms.ChoiceField(
        label="Does the client have 3–6 months of emergency savings?",
        choices=[('yes', 'Yes'), ('no', 'No')]
    )

    # ── Step 5: Financial picture (all money fields together) ────────────
    total_investable_assets = forms.DecimalField(
        label="Total investable assets (R)",
        min_value=0,
        decimal_places=2,
        required=False,  # allowed blank on draft
        help_text="Approximate total value of all investments, savings, and liquid assets"
    )
    monthly_surplus = forms.DecimalField(
        label="Monthly surplus (R)",
        decimal_places=2,
        required=False,
        help_text="Monthly income minus all expenses — what's left over each month"
    )
    financial_goal_amount = forms.DecimalField(
        label="Financial goal amount (R)",
        min_value=0,
        decimal_places=2,
        required=False,
        help_text="The rand amount the client wants to reach"
    )
    has_liabilities = forms.ChoiceField(
        label="Does the client have significant debt?",
        choices=[('yes', 'Yes — home loan, vehicle finance, credit cards etc.'), ('no', 'No significant debt')],
        required=False
    )
    number_of_dependants = forms.IntegerField(
        label="Number of financial dependants",
        min_value=0,
        required=False,
        help_text="People financially dependent on the client (spouse, children, parents)"
    )

    # ── Step 6: Risk capacity ─────────────────────────────────────────────
    risk_return_aware = forms.ChoiceField(
        label="Does the client understand that higher returns require accepting higher risk?",
        choices=[('yes', 'Yes — they accept this'), ('no', 'No — needs explanation')]
    )