from django.urls import path

from .views import *

urlpatterns = [
    path('packages',             packages, name='packages'),
    path('package/<slug:name>',  package,  name='package'),
]