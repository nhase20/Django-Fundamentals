from django.shortcuts import render, redirect
# from django.contrib.auth.models import User
# from django.contrib.auth import authenticate, login
from .forms import RetailClientForm, InstitutionalClientForm
from .models import RetailClient, Portfolio, AssetManaged, InstitutionalClient


def onboarding(request, client_type):
    if client_type == 'retail':
        FormClass = RetailClientForm
    else:
        FormClass = InstitutionalClientForm

    if request.method == 'POST':
        form = FormClass(request.POST)
        
        if form.is_valid():
            client = form.save()
            # username = request.POST.get("username")
            # password = request.POST.get("password")
            # user = User.objects.create_user(
            #         username=username,
            #         password=password
            #     )
            # client.user = user
            # client.save()

            if client_type == 'retail':
                return redirect('retail-dashboard', client_id=client.id)
            else:
                return redirect('institutional-dashboard', client_id=client.id)
    else:
        form = FormClass(initial={'client_type': client_type})

    return render(request, 'retail-form.html' if client_type == 'retail' else 'institutional-form.html', {'form': form})

def home(request):
    # if request.method == "POST":
    #     username = request.POST["username"]
    #     password = request.POST["password"]

    #     user = authenticate(request, username=username, password=password)

    #     if user is not None:
    #         login(request, user)

    #         if user.profile.client_type == "retail":
    #             return redirect("retail-dashboard", client_id=user.profile.client_id)
    #         else:
    #             return redirect("institutional-dashboard", client_id=user.profile.client_id)

    #     return render(request, "login.html", {"error": "Invalid credentials"})

    return render(request, "login.html")


def retail_dashboard(request, client_id):

    client = RetailClient.objects.get(id=client_id)
    portfolio, created = Portfolio.objects.get_or_create(retail_client=client)
    assets = AssetManaged.objects.filter(portfolio=portfolio)

    context = {
        'client': client,
        'portfolio': portfolio,
        'assets': assets
    }
    return render(request, 'retail-dashboard.html', context)

def institutional_dashboard(request, client_id):

    client = InstitutionalClient.objects.get(id=client_id)
    portfolio, created = Portfolio.objects.get_or_create(institutional_client=client)
    assets = AssetManaged.objects.filter(portfolio=portfolio)
    context = {
        'client': client,
        'portfolio': portfolio,
        'assets': assets
    }

    return render(request, 'institutional-dashboard.html', context)