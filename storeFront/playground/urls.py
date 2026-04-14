from django.urls import path
from . import views # to reference view methods in this file

# Make lowercase variables since django looks for them
# This is a URLConf object, which is used to map URLs to views.
urlpatterns = [
    # used to call a URL pattern object, which is used to map a URL to a view function. 
    # The first argument is the URL pattern
    # The second argument is the view function that should be called when the URL is accessed.
    path('hello/', views.say_hello_template),

]
