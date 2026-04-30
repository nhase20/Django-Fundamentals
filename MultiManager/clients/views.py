# clients/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, logout
from django.db.models import Count
from .forms import ClientQuestionnaireForm
from .models import Portfolio, AssetManaged, Profile, Client, Advisor, CLIENT_GROUP_CHOICES
from .automations import dynamic_asset_allocation, generate_client_insights, calculate_risk_profile
import json


# ── Login ──────────────────────────────────────────────────────────────────────
def home(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if hasattr(user, 'advisor'):
                return redirect('create_client')
            elif user.is_staff:
                return redirect('admin_overview')
            else:
                return redirect('dashboard')
        return render(request, "login.html", {"error": "Invalid credentials"})
    return render(request, "login.html")


# ── Logout ─────────────────────────────────────────────────────────────────────
def logout_view(request):
    logout(request)
    return redirect('home')


# ── Advisor registration ────────────────────────────────────────────────────────
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


# ── Advisor: create a client ────────────────────────────────────────────────────
@login_required
def create_client(request):
    if not hasattr(request.user, 'advisor'):
        return redirect('dashboard')

    advisor = request.user.advisor

    if request.method == 'POST':
        form = ClientQuestionnaireForm(request.POST)
        if form.is_valid():
            answers = form.cleaned_data
            risk_profile, asisa_category = calculate_risk_profile(answers)

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
            )

            return redirect('portfolio_results', client_id=client.id)
    else:
        form = ClientQuestionnaireForm()

    return render(request, 'questionnaire.html', {'form': form, 'advisor': advisor})


# ── Advisor dashboard ───────────────────────────────────────────────────────────
@login_required
def advisor_dashboard(request):
    if not hasattr(request.user, 'advisor'):
        return redirect('dashboard')
    if request.user.is_staff and not hasattr(request.user, 'advisor'):
        return redirect('admin_overview')
    
    advisor = request.user.advisor
    clients = Client.objects.filter(advisor=advisor).order_by('name')

    return render(request, 'dashboard.html', {
        'advisor': advisor,
        'clients': clients,
    })


@login_required
def client_detail(request, client_id):
    if not hasattr(request.user, 'advisor') and not request.user.is_staff:
        return redirect('home')
    client = get_object_or_404(Client, id=client_id)
    if hasattr(request.user, 'advisor') and client.advisor != request.user.advisor:
        return redirect('advisor_dashboard')

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
            except Portfolio.DoesNotExist:
                pass
        print('Das Goodt')
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


# ── Client dashboard ────────────────────────────────────────────────────────────
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


# ── Portfolio results ───────────────────────────────────────────────────────────
@login_required
def portfolio_results(request, client_id):
    client = Client.objects.get_object_or_404(id=client_id)

    group_portfolios = Portfolio.objects.filter(
        client_group__iexact=client.client_group,
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

@login_required
def portfolio_list(request):
    if not hasattr(request.user, 'advisor'):
        return redirect('dashboard')

    advisor = request.user.advisor

    GRAVITON_GROUPS = [
    'Graviton', 'Graviton Wealth', 'Graviton Absolute Funds',
    'Graviton Global Funds', 'Graviton Hedge Funds', 'Graviton Hybrid Funds',
    'Graviton Offshore (Franchises)', 'Graviton Retirement Solution',
    'Graviton Shariah Funds', 'Graviton Wealth (Franchises)',
    'Graviton Wealth Management',
    ]

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


def about(request):
    return render(request, 'about.html')