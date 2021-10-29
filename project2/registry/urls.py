from django.urls import path

from .views import *

urlpatterns = [
    path('package', package, name='package'),
]