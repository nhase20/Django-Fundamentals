from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from .forms import RetailClientForm, InstitutionalClientForm
from .models import Portfolio, AssetManaged, Profile

# Method to onboard clients into the app (Information), 
@login_required
def onboarding(request, client_type):
    # First separate type of client user chose, which button user presed between the 2 clients determines path
    if client_type == 'retail':
        FormClass = RetailClientForm 
    else:
        FormClass = InstitutionalClientForm
    
    # After user submits form, thi follows
    if request.method == 'POST':
        form = FormClass(request.POST)
        
        if form.is_valid():
            
            # Custom credentials from user for user authentication
            username = request.POST.get("username")
            password = request.POST.get("password")

            # Create user, once
            if User.objects.filter(username=username).exists():
                form.add_error(None, "Username already exists")
                return render(request, 'retail-form.html', {'form': form})
            
            # Create Django user
            user = User.objects.create_user(username=username,password=password)
            login(request, user) # request.user = user, basically pointing the created user to the request user as they need to be the same
            profile, created = Profile.objects.get_or_create(user=user) # profile creation

            # Creating a client ( From the information filled in from the form)
            client = form.save(commit=False) 
            client.user = user
            client.save() # Save client in DB
            
            # Depending on type of client map the profile to the client (link)
            if client_type == 'retail':
                profile.retail_client = client
                profile.save() # saving profile to DB
                return redirect('retail-dashboard') # head straight to the Retail Dashboard 
            else:
                profile.institutional_client = client
                profile.save()
                return redirect('institutional-dashboard')
        else:
            print("FORM ERRORS:", form.errors)
            print("NON FIELD ERRORS:", form.non_field_errors())
    else:
        form = FormClass(initial={'client_type': client_type})

    # Refresh page if anything else happens
    return render(request, 'retail-form.html' if client_type == 'retail' else 'institutional-form.html', {'form': form})


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

            if profile.retail_client:
                return redirect("retail-dashboard")
            
            elif profile.institutional_client:
                return redirect("institutional-dashboard")

            else:
                # user exists but hasn't onboarded yet
                return redirect("onboarding", client_type="retail")

        # Error Handling
        return render(request, "login.html", {"error": "Invalid credentials"})

    return render(request, "login.html")

# Action to move to Dashboard for Retail Clients
@login_required
def retail_dashboard(request):

    # Get client info
    client = request.user.profile.retail_client
    portfolio, created = Portfolio.objects.get_or_create(retail_client=client)
    assets = AssetManaged.objects.filter(portfolio=portfolio)


    context = {
        'client': client,
        'portfolio': portfolio,
        'assets': assets
    }
    # After getting info move to Retail dashboard template
    return render(request, 'retail-dashboard.html', context)

# Action to move to User Dashboard for Institutional Clients
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
    # After getting info move to Institutional dashboard template
    return render(request, 'institutional-dashboard.html', context)

# Action to move to About page 
def about(request):
    return render(request, 'about.html')