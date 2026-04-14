from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
# A view is a function or method that takes http requests as arguments, imports the relevant model(s), 
# and finds out what data to send to the template, and returns the final result.

def say_hello(request):
    return HttpResponse('Hello World!')
# From here you map the view to a URL so that when a user visits that URL, the view is called and the response is returned to the user.
# You can also use the render function to render a template and return an HttpResponse object with the rendered text.
def say_hello_template(request):
    return render(request, 'hello.html', {'name': 'Money'})
