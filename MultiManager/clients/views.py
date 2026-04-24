# clients/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login
from django.db.models import Count
from .forms import ClientForm
from .models import Portfolio, AssetManaged, Profile, Client
from .automations import dynamic_asset_allocation, generate_client_insights
import json


def onboarding(request):
    FormClass = ClientForm
    if request.method == 'POST':
        form = FormClass(request.POST)
        if form.is_valid():
            username = request.POST.get("username")
            password = request.POST.get("password")
            if User.objects.filter(username=username).exists():
                return render(request, 'form.html', {
                    'form': form,
                    'error': 'That username is already taken.'
                })
            user = User.objects.create_user(username=username, password=password)
            login(request, user)
            profile, _ = Profile.objects.get_or_create(user=user)
            client = form.save(commit=False)
            client.user = user
            client.save()
            profile.client = client
            profile.save()
            return redirect('dashboard')
        else:
            print("FORM ERRORS:", form.errors)
    else:
        form = FormClass()
    return render(request, 'form.html', {'form': form})


def home(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Admin goes straight to the overview
            if user.is_staff:
                return redirect("admin_overview")
            profile = user.profile
            if profile.client:
                return redirect("dashboard")
            else:
                return redirect("onboarding")
        return render(request, "login.html", {"error": "Invalid credentials"})
    return render(request, "login.html")


@login_required
def dashboard(request):
    client = request.user.profile.client
    portfolio, _ = Portfolio.objects.get_or_create(client=client)
    assets = AssetManaged.objects.filter(portfolio=portfolio)
    recommended_portfolios = Portfolio.portfolioName(client)

    # allocating unique to this client
    allocation = dynamic_asset_allocation(client)
    allocation_json = json.dumps(allocation)

    insights = generate_client_insights(client)

    context = {
        'client':                 client,
        'portfolio':              portfolio,
        'recommended_portfolios': recommended_portfolios,
        'assets':                 assets,
        'allocation_json':        allocation_json,
        'allocation':             allocation,
        'insights':               insights,
    }
    return render(request, 'dashboard.html', context)

@staff_member_required
def admin_overview(request):
    all_clients = Client.objects.all()
    total = all_clients.count()

    # ── Profile distribution ──
    profile_dist = (
        all_clients
        .values('risk_profile')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    # ── Client group distribution ──
    group_dist = (
        all_clients
        .values('client_group')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    # ── Risk rating distribution ──
    rating_dist = (
        all_clients
        .values('risk_rating')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    # ── Portfolio match stats — how many clients share the same portfolio name ──
    portfolio_dist = (
        Portfolio.objects
        .filter(client__isnull=False)   # only client-assigned portfolios
        .values('name')
        .annotate(count=Count('id'))
        .order_by('-count')[:15]        # top 15
    )

    # ── Time horizon buckets ──
    short   = all_clients.filter(time_horizon__lt=5).count()
    medium  = all_clients.filter(time_horizon__gte=5,  time_horizon__lt=10).count()
    long    = all_clients.filter(time_horizon__gte=10, time_horizon__lt=20).count()
    vlong   = all_clients.filter(time_horizon__gte=20).count()

    horizon_buckets = [
        {"label": "Short (< 5 yrs)",    "count": short},
        {"label": "Medium (5–9 yrs)",   "count": medium},
        {"label": "Long (10–19 yrs)",   "count": long},
        {"label": "Very Long (20+ yrs)","count": vlong},
    ]

    # ── Age buckets ──
    age_u30  = all_clients.filter(age__lt=30).count()
    age_3045 = all_clients.filter(age__gte=30, age__lt=45).count()
    age_4560 = all_clients.filter(age__gte=45, age__lt=60).count()
    age_o60  = all_clients.filter(age__gte=60).count()

    age_buckets = [
        {"label": "Under 30","count": age_u30},
        {"label": "30–44", "count": age_3045},
        {"label": "45–59", "count": age_4560},
        {"label": "60+",  "count": age_o60},
    ]
    profile_labels = json.dumps([r['risk_profile'] for r in profile_dist])
    profile_counts = json.dumps([r['count'] for r in profile_dist])
    group_labels   = json.dumps([r['client_group'] for r in group_dist])
    group_counts   = json.dumps([r['count'] for r in group_dist])
    horizon_labels = json.dumps([b['label'] for b in horizon_buckets])
    horizon_counts = json.dumps([b['count'] for b in horizon_buckets])
    age_labels     = json.dumps([b['label']  for b in age_buckets])
    age_counts     = json.dumps([b['count']  for b in age_buckets])

    context = {
        'total': total,
        'all_clients': all_clients.order_by('name'),
        'profile_dist': profile_dist,
        'group_dist': group_dist,
        'rating_dist': rating_dist,
        'portfolio_dist': portfolio_dist,
        'horizon_buckets':horizon_buckets,
        'age_buckets': age_buckets,
        # chart data
        'profile_labels': profile_labels,
        'profile_counts': profile_counts,
        'group_labels': group_labels,
        'group_counts':  group_counts,
        'horizon_labels': horizon_labels,
        'horizon_counts':   horizon_counts,
        'age_labels': age_labels,
        'age_counts': age_counts,
    }
    return render(request, 'admin_overview.html', context)


def about(request):
    return render(request, 'about.html')