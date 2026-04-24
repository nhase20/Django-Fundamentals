from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from .forms import ClientForm
from .models import Portfolio, AssetManaged, Profile
from .automations import retail_asset_allocation 
import json 

# Method to onboard clients into the app (Information), 
def onboarding(request):
    # Find client form
    FormClass = ClientForm
    
    # After user submits form, this follows
    if request.method == 'POST':
        form = FormClass(request.POST)
        
        if form.is_valid():
            
            # Custom credentials from user for user authentication
            username = request.POST.get("username")
            password = request.POST.get("password")
            
            # Create Django user
            user = User.objects.create_user(username=username,password=password)
            login(request, user) # request.user = user, basically pointing the created user to the request user as they need to be the same
            profile, created = Profile.objects.get_or_create(user=user) # profile creation

            # Creating a client ( From the information filled in from the form)
            client = form.save(commit=False) 
            client.user = user
            client.save() # Save client in DB
            
            profile.client = client
            profile.save() # saving profile to DB
            return redirect('dashboard') # head straight to the  Dashboard 

        else:
            print("FORM ERRORS:", form.errors)
            print("NON FIELD ERRORS:", form.non_field_errors())
    
    else:
        form = FormClass()

    # Refresh page if anything else happens
    return render(request,'form.html', {'form': form})


# Method to log in clients who are users
def home(request):
    if request.method == "POST":
        
        # Get Credentials from user
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Check and find user from DB
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Match users
            login(request, user)

            # get user profile in order to navigate to client
            profile = user.profile

            if profile.client:
                return redirect("dashboard")

            else:
                # user exists but hasn't onboarded yet
                return redirect("onboarding")

        # Error Handling
        return render(request, "login.html", {"error": "Invalid credentials"})

    return render(request, "login.html")

# Action to move to Dashboard for Clients
@login_required
def dashboard(request):

    # Get client info
    client = request.user.profile.client
    portfolio, created = Portfolio.objects.get_or_create(client=client)
    assets = AssetManaged.objects.filter(portfolio=portfolio)
    recommended_portfolios = portfolio.portfolioName(client)

    allocation = retail_asset_allocation(client)
    allocation_json = json.dumps(allocation)

    context = {
        'client': client,
        'portfolio': portfolio,
        'recommended_portfolios': recommended_portfolios,
        'allocation_json': allocation_json,
        'assets': assets
    }
    # After getting info move to Retail dashboard template
    return render(request, 'dashboard.html', context)

# Action to move to About page 
def about(request):
    return render(request, 'about.html')