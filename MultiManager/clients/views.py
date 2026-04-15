from django.shortcuts import render, redirect
from .forms import RetailClientForm, InstitutionalClientForm
from .models import RetailClient, Portfolio, AssetManaged, InstitutionalClient

def home(request):
    return render(request, 'login.html')


def onboarding(request, client_type):
    if client_type == 'retail':
        FormClass = RetailClientForm
    else:
        FormClass = InstitutionalClientForm

    if request.method == 'POST':
        form = FormClass(request.POST)
        if form.is_valid():
            client = form.save()

            if client_type == 'retail':
                return redirect('retail-dashboard', client_id=client.id)
            else:
                return redirect('institutional-dashboard', client_id=client.id)
    else:
        form = FormClass(initial={'client_type': client_type})

    return render(request, 'retail-form.html' if client_type == 'retail' else 'institutional-form.html', {'form': form})

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
    portfolio, created = Portfolio.objects.get_or_create(retail_client=client)
    assets = AssetManaged.objects.filter(portfolio=portfolio)
    context = {
        'client': client,
        'portfolio': portfolio,
        'assets': assets
    }

    return render(request, 'institutional-dashboard.html', context)