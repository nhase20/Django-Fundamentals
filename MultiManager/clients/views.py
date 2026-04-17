from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from .forms import RetailClientForm, InstitutionalClientForm
from .models import Portfolio, AssetManaged, Profile

@login_required
def onboarding(request, client_type):
    if client_type == 'retail':
        FormClass = RetailClientForm
    else:
        FormClass = InstitutionalClientForm
    
    if request.method == 'POST':
        form = FormClass(request.POST)
        
        if form.is_valid():
            
            username = request.POST.get("username")
            password = request.POST.get("password")

            # 1. Create user (ONLY ONCE)
            if User.objects.filter(username=username).exists():
                form.add_error(None, "Username already exists")
                return render(request, 'retail-form.html', {'form': form})
            
            # Create Django user
            user = User.objects.create_user(username=username,password=password)
            login(request, user)
            profile, created = Profile.objects.get_or_create(user=user)
            client = form.save(commit=False)
            client.user = user
            client.save()
            
            
            if client_type == 'retail':
                profile.retail_client = client
                profile.save()
                return redirect('retail-dashboard')
            else:
                profile.institutional_client = client
                profile.save()
                return redirect('institutional-dashboard')
        else:
            print("FORM ERRORS:", form.errors)
            print("NON FIELD ERRORS:", form.non_field_errors())
    else:
        form = FormClass(initial={'client_type': client_type})

    return render(request, 'retail-form.html' if client_type == 'retail' else 'institutional-form.html', {'form': form})


def home(request):
    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            profile = user.profile

            if profile.retail_client:
                return redirect("retail-dashboard")
            
            elif profile.institutional_client:
                return redirect("institutional-dashboard")

            else:
                # user exists but hasn't onboarded yet
                return redirect("onboarding", client_type="retail")


        return render(request, "login.html", {"error": "Invalid credentials"})

    return render(request, "login.html")

@login_required
def retail_dashboard(request):

    client = request.user.profile.retail_client

    portfolio, created = Portfolio.objects.get_or_create(retail_client=client)
    assets = AssetManaged.objects.filter(portfolio=portfolio)


    context = {
        'client': client,
        'portfolio': portfolio,
        'assets': assets
    }
    return render(request, 'retail-dashboard.html', context)

@login_required
def institutional_dashboard(request):

    client = request.user.profile.institutional_client
    portfolio, created = Portfolio.objects.get_or_create(institutional_client=client)
    assets = AssetManaged.objects.filter(portfolio=portfolio)
    context = {
        'client': client,
        'portfolio': portfolio,
        'assets': assets
    }

    return render(request, 'institutional-dashboard.html', context)