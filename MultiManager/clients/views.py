from django.shortcuts import render, redirect
from .forms import RetailClientForm, InstitutionalClientForm

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

            if client.client_type == 'retail':
                return redirect('retail-dashboard')
            else:
                return redirect('institutional-dashboard')
    else:
        form = FormClass(initial={'client_type': client_type})

    return render(request, 'retail-form.html' if client_type == 'retail' else 'institutional-form.html', {'form': form})


def retail_dashboard(request):
    return render(request, 'retail-dashboard.html')


def institutional_dashboard(request):
    return render(request, 'institutional-dashboard.html')