from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, logout
from django.db.models import Count
from .forms import ClientQuestionnaireForm
from .models import Portfolio, Client, Advisor, CLIENT_GROUP_CHOICES
from .automations import dynamic_asset_allocation, generate_client_insights, calculate_risk_profile
import json


def home(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if hasattr(user, 'advisor'):
                return redirect('dashboard')
            elif user.is_staff:
                return redirect('admin_overview')
            else:
                return redirect('dashboard')
        return render(request, "login.html", {"error": "Invalid credentials"})
    return render(request, "login.html")


def logout_view(request):
    logout(request)
    return redirect('home')


def register_advisor(request):
    if request.method == "POST":
        first_name     = request.POST.get("first_name", "").strip()
        last_name      = request.POST.get("last_name", "").strip()
        username       = request.POST.get("username", "").strip()
        password       = request.POST.get("password", "").strip()
        password2      = request.POST.get("password2", "").strip()
        business_group = request.POST.get("business_group", "").strip()

        errors = {}
        if not first_name:
            errors["first_name"] = "First name is required."
        if not last_name:
            errors["last_name"] = "Last name is required."
        if not username:
            errors["username"] = "Username is required."
        elif User.objects.filter(username=username).exists():
            errors["username"] = "That username is already taken."
        if len(password) < 8:
            errors["password"] = "Password must be at least 8 characters."
        if password != password2:
            errors["password2"] = "Passwords do not match."
        if not business_group:
            errors["business_group"] = "Please select a business group."

        if errors:
            return render(request, "register_advisor.html", {
                "errors": errors,
                "groups": CLIENT_GROUP_CHOICES,
                "form_data": request.POST,
            })

        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        Advisor.objects.create(user=user, business_group=business_group)
        login(request, user)
        return redirect('create_client')

    return render(request, "register_advisor.html", {
        "groups": CLIENT_GROUP_CHOICES,
        "form_data": {},
        "errors": {},
    })


@login_required
def create_client(request):
    if not hasattr(request.user, 'advisor'):
        return redirect('dashboard')

    advisor = request.user.advisor

    if request.method == 'POST':
        action = request.POST.get('action', 'active')  # 'draft' or 'active'

        def safe_int(val, default=0):
            try: return int(val)
            except (ValueError, TypeError): return default

        def safe_decimal(val):
            try:
                from decimal import Decimal
                return Decimal(str(val)) if val else None
            except Exception: return None

        if action == 'draft':
            name = request.POST.get('name', '').strip()
            if not name:
                messages.error(request, 'Please enter a client name before saving a draft.')
                return render(request, 'questionnaire.html', {
                    'form': ClientQuestionnaireForm(request.POST),
                    'advisor': advisor,
                })

            horizon_map = {'short': 3, 'medium': 7, 'long': 15}
            has_liabilities_raw = request.POST.get('has_liabilities', '')

            client = Client.objects.create(
                name=name,
                age=safe_int(request.POST.get('age'), 18),
                investment_goal=request.POST.get('purpose', 'None') or 'None',
                time_horizon=horizon_map.get(request.POST.get('time_horizon', ''), 7),
                questionnaire_status='DRAFT',
                questionnaire_step=int(request.POST.get('current_step', 1)),
                client_group=advisor.business_group,
                advisor=advisor,
                risk_profile='',
                risk_tolerance='',
                risk_rating='medium',
                # financial fields — save whatever is present
                total_investable_assets=safe_decimal(request.POST.get('total_investable_assets')),
                monthly_surplus=safe_decimal(request.POST.get('monthly_surplus')),
                financial_goal_amount=safe_decimal(request.POST.get('financial_goal_amount')),
                has_liabilities=True if has_liabilities_raw == 'yes' else (False if has_liabilities_raw == 'no' else None),
                number_of_dependants=safe_int(request.POST.get('number_of_dependants'), None) if request.POST.get('number_of_dependants') else None,
            )
            messages.success(request, f'Draft saved for {client.name}. You can complete this later from the dashboard.')
            return redirect('advisor_dashboard')

        # action == 'active' — full validation
        form = ClientQuestionnaireForm(request.POST)
        if form.is_valid():
            answers = form.cleaned_data
            from .automations import calculate_risk_profile
            risk_profile, asisa_category = calculate_risk_profile(answers)

            has_liabilities_val = answers.get('has_liabilities')
            client = Client.objects.create(
                name=answers['name'],
                age=answers['age'],
                investment_goal=answers['purpose'],
                time_horizon={'short': 3, 'medium': 7, 'long': 15}[answers['time_horizon']],
                client_group=advisor.business_group,
                advisor=advisor,
                risk_profile=risk_profile,
                risk_tolerance=asisa_category,
                risk_rating='medium',
                questionnaire_status='ONGOING',
                total_investable_assets=answers.get('total_investable_assets'),
                monthly_surplus=answers.get('monthly_surplus'),
                financial_goal_amount=answers.get('financial_goal_amount'),
                has_liabilities=True if has_liabilities_val == 'yes' else (False if has_liabilities_val == 'no' else None),
                number_of_dependants=answers.get('number_of_dependants'),
            )
            return redirect('portfolio_results', client_id=client.id)
        else:
            return render(request, 'questionnaire.html', {'form': form, 'advisor': advisor})

    return render(request, 'questionnaire.html', {
        'form': ClientQuestionnaireForm(),
        'advisor': advisor,
    })


@login_required
def advisor_dashboard(request):
    if not hasattr(request.user, 'advisor'):
        return redirect('dashboard')
    if request.user.is_staff and not hasattr(request.user, 'advisor'):
        return redirect('admin_overview')
    
    advisor = request.user.advisor
    draft_clients   = Client.objects.filter(
        advisor=advisor, questionnaire_status__in=['DRAFT', 'ONGOING']
    ).order_by('name')
    active_clients    = Client.objects.filter(advisor=advisor, questionnaire_status='ACTIVE').order_by('name')
    

    return render(request, 'dashboard.html', {
        'advisor': advisor,
        'draft_clients':     draft_clients,
        'active_clients':    active_clients,
        'clients': active_clients,
    })


@login_required
def client_detail(request, client_id):
    if not hasattr(request.user, 'advisor') and not request.user.is_staff:
        return redirect('home')
    client = get_object_or_404(Client, id=client_id)
    if hasattr(request.user, 'advisor') and client.advisor != request.user.advisor:
        return redirect('advisor_dashboard')
    
    if client.questionnaire_status == 'DRAFT':
        messages.warning(
            request,
            f'{client.name} is an incomplete draft. Please complete the questionnaire first.'
        )
        return redirect('resume_client', client_id=client.id)

    allocation = dynamic_asset_allocation(client)

    raw_insights   = generate_client_insights(client)
    insights = [
    {
        "label": "Portfolio Suitability",
        "value": raw_insights["suitability"],
        "explanation": "Recommended strategy based on client profile."
    },
    {
        "label": "Investment Reasoning",
        "value": "",
        "explanation": raw_insights["reasoning"]
    },
    {
        "label": "Benchmark",
        "value": raw_insights["benchmark"],
        "explanation": "Reference index used to evaluate performance."
    },
    {
        "label": raw_insights["scenario"]['label'],
        "value": "Probability "+ raw_insights["scenario"]["probability"],
        "explanation": raw_insights["scenario"]["description"] +" -- {"+raw_insights["scenario"]["return_range"]+"}"
    },
]

    assigned_portfolios = Portfolio.objects.filter(client=client)

    group_portfolios = Portfolio.objects.filter(
        client_group__iexact=client.client_group,
        risk_profile__iexact=client.risk_profile,
        fund_category__iexact=client.risk_tolerance,
    )

    if group_portfolios.exists():
        recommended = group_portfolios
        source = 'group'
    else:
        graviton_groups = [
            'Graviton','Graviton Wealth','Graviton Absolute Funds','Graviton Global Funds',
            'Graviton Hedge Funds','Graviton Hybrid Funds','Graviton Offshore (Franchises)',
            'Graviton Retirement Solution','Graviton Shariah Funds',
            'Graviton Wealth (Franchises)','Graviton Wealth Management',
        ]
        recommended = Portfolio.objects.filter(
            client_group__in=graviton_groups,
            risk_profile__iexact=client.risk_profile,
            fund_category__iexact=client.risk_tolerance,
        )
        source = 'graviton'

    return render(request, 'client_detail.html', {
        'client':               client,
        'allocation':           allocation,
        'allocation_json':      allocation,
        'insights':             insights,
        'assigned_portfolios':  assigned_portfolios,
        'recommended':          recommended,
        'source':               source,
    })

@login_required
def edit_client(request, client_id):
    if not hasattr(request.user, 'advisor') and not request.user.is_staff:
        return redirect('home')
    client = get_object_or_404(Client, id=client_id)
    if hasattr(request.user, 'advisor') and client.advisor != request.user.advisor:
        return redirect('advisor_dashboard')

    if request.method == 'POST':
        client.name            = request.POST.get('name', client.name).strip()
        client.age             = int(request.POST.get('age', client.age))
        client.investment_goal = request.POST.get('investment_goal', client.investment_goal).strip()
        client.time_horizon    = int(request.POST.get('time_horizon', client.time_horizon))
        client.risk_profile    = request.POST.get('risk_profile', client.risk_profile)
        client.risk_tolerance  = request.POST.get('risk_tolerance', client.risk_tolerance)
        client.risk_rating     = request.POST.get('risk_rating', client.risk_rating)
        client.client_group    = request.POST.get('client_group', client.client_group)
        client.save()
        return redirect('client_detail', client_id=client.id)

    return render(request, 'edit_client.html', {
        'client':                   client,
        'risk_profile_choices':     Client.RISK_PROFILE,
        'risk_tolerance_choices':   Client.RISK_TOLERANCE,
        'risk_rating_choices':      Client.RISK_RATING,
        'group_choices':            CLIENT_GROUP_CHOICES,
    })


@login_required
def add_portfolio(request, client_id):
    if not hasattr(request.user, 'advisor') and not request.user.is_staff:
        return redirect('home')
    client = get_object_or_404(Client, id=client_id)
    if hasattr(request.user, 'advisor') and client.advisor != request.user.advisor:
        return redirect('advisor_dashboard')

    if request.method == 'POST':
        portfolio_id = request.POST.get('portfolio_id')
        if portfolio_id:
            try:
                portfolio = Portfolio.objects.get(id=portfolio_id)
                Portfolio.objects.filter(client=client).update(client=None)
                portfolio.client = client
                portfolio.save()
                client.questionnaire_status = 'ACTIVE'
                client.save(update_fields=['questionnaire_status'])
            except Portfolio.DoesNotExist:
                pass
        return redirect('client_detail', client_id=client.id)
    
    print('Passed stage')
    group_portfolios = Portfolio.objects.filter(
        client_group__iexact=client.client_group,
        risk_profile__iexact=client.risk_profile,
        fund_category__iexact=client.risk_tolerance,
    )
    if not group_portfolios.exists():
        graviton_groups = [
            'Graviton','Graviton Wealth','Graviton Absolute Funds','Graviton Global Funds',
            'Graviton Hedge Funds','Graviton Hybrid Funds','Graviton Offshore (Franchises)',
            'Graviton Retirement Solution','Graviton Shariah Funds',
            'Graviton Wealth (Franchises)','Graviton Wealth Management',
        ]
        group_portfolios = Portfolio.objects.filter(
            client_group__in=graviton_groups,
            risk_profile__iexact=client.risk_profile,
            fund_category__iexact=client.risk_tolerance,
        )

    return render(request, 'add_portfolio.html', {
        'client': client, 'portfolios': group_portfolios,
    })


@login_required
def dashboard(request):
    if hasattr(request.user, 'advisor'):
        return redirect('advisor_dashboard')

    try:
        client = request.user.profile.client
    except Exception:
        return redirect('home')

    allocation  = dynamic_asset_allocation(client)
    insights    = generate_client_insights(client)
    recommended = Portfolio.portfolioName(client)

    return render(request, 'dashboard.html', {
        'client':                 client,
        'allocation':             allocation,
        'allocation_json':        json.dumps(allocation),
        'insights':               insights,
        'recommended_portfolios': recommended,
    })


@login_required
def portfolio_results(request, client_id):
    client = get_object_or_404(Client,id=client_id)

    group_portfolios = Portfolio.objects.filter(
        client_group__iexact=client.client_group,
        risk_profile__iexact=client.risk_profile,
        fund_category__iexact=client.risk_tolerance,
    )

    if group_portfolios.exists():
        recommended = group_portfolios
        source = 'group'
    else:
        graviton_groups = [
            'Graviton', 'Graviton Wealth', 'Graviton Absolute Funds',
            'Graviton Global Funds', 'Graviton Hedge Funds', 'Graviton Hybrid Funds',
            'Graviton Offshore (Franchises)', 'Graviton Retirement Solution',
            'Graviton Shariah Funds', 'Graviton Wealth (Franchises)',
            'Graviton Wealth Management',
        ]
        recommended = Portfolio.objects.filter(
            client_group__in=graviton_groups,
            risk_profile__iexact=client.risk_profile,
            fund_category__iexact=client.risk_tolerance,
        )
        source = 'graviton'

    return render(request, 'portfolio.html', {
        'client':      client,
        'recommended': recommended,
        'source':      source,
    })


# ── Admin overview ──────────────────────────────────────────────────────────────
@staff_member_required
def admin_overview(request):
    all_clients = Client.objects.all()
    total = all_clients.count()

    profile_dist   = all_clients.values('risk_profile').annotate(count=Count('id')).order_by('-count')
    group_dist     = all_clients.values('client_group').annotate(count=Count('id')).order_by('-count')
    rating_dist    = all_clients.values('risk_rating').annotate(count=Count('id')).order_by('-count')
    portfolio_dist = (Portfolio.objects.filter(client__isnull=False)
                      .values('name').annotate(count=Count('id')).order_by('-count')[:15])

    short  = all_clients.filter(time_horizon__lt=5).count()
    medium = all_clients.filter(time_horizon__gte=5,  time_horizon__lt=10).count()
    long_  = all_clients.filter(time_horizon__gte=10, time_horizon__lt=20).count()
    vlong  = all_clients.filter(time_horizon__gte=20).count()

    horizon_buckets = [
        {"label": "Short (< 5 yrs)",     "count": short},
        {"label": "Medium (5–9 yrs)",    "count": medium},
        {"label": "Long (10–19 yrs)",    "count": long_},
        {"label": "Very Long (20+ yrs)", "count": vlong},
    ]
    age_buckets = [
        {"label": "Under 30", "count": all_clients.filter(age__lt=30).count()},
        {"label": "30–44",    "count": all_clients.filter(age__gte=30, age__lt=45).count()},
        {"label": "45–59",    "count": all_clients.filter(age__gte=45, age__lt=60).count()},
        {"label": "60+",      "count": all_clients.filter(age__gte=60).count()},
    ]

    context = {
        'total': total,
        'all_clients': all_clients.order_by('name'),
        'profile_dist': profile_dist, 'group_dist': group_dist,
        'rating_dist': rating_dist, 'portfolio_dist': portfolio_dist,
        'horizon_buckets': horizon_buckets, 'age_buckets': age_buckets,
        'profile_labels': json.dumps([r['risk_profile'] for r in profile_dist]),
        'profile_counts': json.dumps([r['count'] for r in profile_dist]),
        'group_labels':   json.dumps([r['client_group'] for r in group_dist]),
        'group_counts':   json.dumps([r['count'] for r in group_dist]),
        'horizon_labels': json.dumps([b['label'] for b in horizon_buckets]),
        'horizon_counts': json.dumps([b['count'] for b in horizon_buckets]),
        'age_labels':     json.dumps([b['label'] for b in age_buckets]),
        'age_counts':     json.dumps([b['count'] for b in age_buckets]),
    }
    return render(request, 'admin_overview.html', context)

GRAVITON_GROUPS = [
    'Graviton', 'Graviton Wealth', 'Graviton Absolute Funds',
    'Graviton Global Funds', 'Graviton Hedge Funds', 'Graviton Hybrid Funds',
    'Graviton Offshore (Franchises)', 'Graviton Retirement Solution',
    'Graviton Shariah Funds', 'Graviton Wealth (Franchises)',
    'Graviton Wealth Management',
]

@login_required
def portfolio_list(request):
    if not hasattr(request.user, 'advisor'):
        return redirect('dashboard')

    advisor = request.user.advisor

    group_portfolios = Portfolio.objects.filter(
    client_group__iexact=advisor.business_group,
    ).order_by('risk_profile', 'name')

    # Show Graviton fallbacks only when the advisor's own group is not a Graviton group,
    # OR always as a supplementary reference section when they are Graviton.
    graviton_portfolios = Portfolio.objects.filter(
    client_group__in=GRAVITON_GROUPS,
    ).exclude(
    client_group__iexact=advisor.business_group,
    ).order_by('client_group', 'risk_profile', 'name')

    # Unique risk profiles for the filter dropdown
    all_profiles = sorted(set(
    list(group_portfolios.values_list('risk_profile', flat=True)) +
    list(graviton_portfolios.values_list('risk_profile', flat=True))
    ))

    source = 'group' if group_portfolios.exists() else 'graviton'

    return render(request, 'portfolio_list.html', {
    'advisor': advisor,
    'group_portfolios': group_portfolios,
    'graviton_portfolios': graviton_portfolios,
    'risk_profiles': all_profiles,
    'source': source,
    })


@login_required
def create_portfolio(request):

    if not hasattr(request.user, 'advisor'):
        return redirect('dashboard')

    advisor = request.user.advisor

    # Choices pulled from the existing model constants
    risk_profile_choices = Client.RISK_PROFILE   # e.g. [('Conservative','Conservative'), ...]
    asisa_choices        = Client.RISK_TOLERANCE  # e.g. [('(ASISA) South African MA Income', ...), ...]

    if request.method == 'POST':
        name          = request.POST.get('name', '').strip()
        client_group  = request.POST.get('client_group', '').strip()
        risk_profile  = request.POST.get('risk_profile', '').strip()
        fund_category = request.POST.get('fund_category', '').strip()
        total_value   = request.POST.get('total_value', '').strip()

        # Server-side validation
        errors = {}
        if not name:
            errors['name'] = 'Portfolio name is required.'
        if not client_group:
            errors['client_group'] = 'Please select a company.'
        if not risk_profile:
            errors['risk_profile'] = 'Please select a risk profile.'
        if not fund_category:
            errors['fund_category'] = 'Please select an ASISA category.'

        # Check for duplicate name within the same group
        if name and client_group and Portfolio.objects.filter(
            name__iexact=name,
            risk_profile__iexact=risk_profile,
            client_group__iexact=client_group,
        ).exists():
            errors['name'] = f'A portfolio called "{name}" already exists for {client_group}.'

        if errors:
            return render(request, 'create_portfolio.html', {
                'advisor':              advisor,
                'risk_profile_choices': risk_profile_choices,
                'asisa_choices':        asisa_choices,
                'group_choices':        CLIENT_GROUP_CHOICES,
                'error':                'Please fix the errors below.',
                'form_data':            request.POST,
            })

        # Parse optional total_value
        parsed_value = None
        if total_value:
            try:
                parsed_value = float(total_value)
            except ValueError:
                parsed_value = None

        # Save directly to the database
        Portfolio.objects.create(
            name=name,
            client_group=client_group,
            risk_profile=risk_profile,
            fund_category=fund_category,
            total_value=parsed_value if parsed_value is not None else 0,
        )

        messages.success(request, f'Portfolio "{name}" created successfully.')
        return redirect('portfolio_list')

    # GET request — render the blank form
    return render(request, 'create_portfolio.html', {
        'advisor':              advisor,
        'risk_profile_choices': risk_profile_choices,
        'asisa_choices':        asisa_choices,
        'group_choices':        CLIENT_GROUP_CHOICES,
        'form_data':            {},
    })

def about(request):
    return render(request, 'about.html')

@login_required
def mark_completed(request, client_id):
    """Mark a FINAL/ACTIVE client as COMPLETED (filed away)."""
    if not hasattr(request.user, 'advisor'):
        return redirect('dashboard')
    client = get_object_or_404(Client, id=client_id)
    if client.advisor != request.user.advisor:
        return redirect('advisor_dashboard')

    if request.method == 'POST':
        client.questionnaire_status = 'COMPLETED'
        client.save()
        messages.success(request, f'{client.name} has been marked as completed.')
    return redirect('advisor_dashboard')


@login_required
def resume_client(request, client_id):
    """Resume filling in a DRAFT client's questionnaire."""
    if not hasattr(request.user, 'advisor'):
        return redirect('dashboard')
    client = get_object_or_404(Client, id=client_id)
    if client.advisor != request.user.advisor:
        return redirect('advisor_dashboard')

    if client.questionnaire_status != 'DRAFT':
        return redirect('client_detail', client_id=client.id)

    if request.method == 'POST':
        action = request.POST.get('action', 'active')

        def safe_decimal(val):
            try:
                from decimal import Decimal
                return Decimal(str(val)) if val else None
            except Exception: return None

        horizon_map = {'short': 3, 'medium': 7, 'long': 15}

        if action == 'draft':
            # Save progress again, stay DRAFT
            has_liabilities_raw = request.POST.get('has_liabilities', '')
            client.name = request.POST.get('name', client.name).strip() or client.name
            client.age = int(request.POST.get('age', client.age) or client.age)
            client.investment_goal = request.POST.get('purpose', client.investment_goal) or client.investment_goal
            client.time_horizon = horizon_map.get(request.POST.get('time_horizon', ''), client.time_horizon)
            client.total_investable_assets = safe_decimal(request.POST.get('total_investable_assets')) or client.total_investable_assets
            client.monthly_surplus = safe_decimal(request.POST.get('monthly_surplus')) or client.monthly_surplus
            client.financial_goal_amount = safe_decimal(request.POST.get('financial_goal_amount')) or client.financial_goal_amount
            if has_liabilities_raw == 'yes': client.has_liabilities = True
            elif has_liabilities_raw == 'no': client.has_liabilities = False
            dep = request.POST.get('number_of_dependants', '')
            if dep: client.number_of_dependants = int(dep)
            step_val = request.POST.get('current_step', '')
            if step_val:
                client.questionnaire_step = int(step_val)
            client.save()
            messages.success(request, f'Draft updated for {client.name}.')
            return redirect('advisor_dashboard')

        # action == 'active' — full validation, finalise
        form = ClientQuestionnaireForm(request.POST)
        if form.is_valid():
            answers = form.cleaned_data
            from .automations import calculate_risk_profile
            risk_profile, asisa_category = calculate_risk_profile(answers)
            has_liabilities_val = answers.get('has_liabilities')

            client.name = answers['name']
            client.age = answers['age']
            client.investment_goal = answers['purpose']
            client.time_horizon = horizon_map[answers['time_horizon']]
            client.risk_profile = risk_profile
            client.risk_tolerance = asisa_category
            client.risk_rating = 'medium'
            client.questionnaire_status = 'ONGOING'
            client.total_investable_assets = answers.get('total_investable_assets')
            client.monthly_surplus = answers.get('monthly_surplus')
            client.financial_goal_amount = answers.get('financial_goal_amount')
            client.has_liabilities = True if has_liabilities_val == 'yes' else (False if has_liabilities_val == 'no' else None)
            client.number_of_dependants = answers.get('number_of_dependants')
            client.save()
            return redirect('portfolio_results', client_id=client.id)
        else:
            return render(request, 'questionnaire.html', {
                'form': form,
                'advisor': request.user.advisor,
                'resuming_client': client,
            })

    # GET — pre-fill the form with whatever the draft has
    initial = {
        'name': client.name,
        'age': client.age,
        'purpose': client.investment_goal,
        'total_investable_assets': str(client.total_investable_assets) if client.total_investable_assets is not None else '',
        'monthly_surplus': str(client.monthly_surplus) if client.monthly_surplus is not None else '',
        'financial_goal_amount': str(client.financial_goal_amount) if client.financial_goal_amount is not None else '',
        'number_of_dependants': str(client.number_of_dependants) if client.number_of_dependants is not None else '',
        'has_liabilities': 'yes' if client.has_liabilities else ('no' if client.has_liabilities is False else ''),
        # Radio fields that map from model storage back to questionnaire values
        'time_horizon': {3: 'short', 7: 'medium', 15: 'long'}.get(client.time_horizon, ''),
    }
    form = ClientQuestionnaireForm(initial=initial)
    return render(request, 'questionnaire.html', {
        'form': form,
        'advisor': request.user.advisor,
        'resuming_client': client,
        'initial_data': json.dumps(initial),
        'initial_step': client.questionnaire_step,
    })