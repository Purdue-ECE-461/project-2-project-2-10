from django.urls import path

from .views import *

urlpatterns = [
    path('packages',             packages,  name='packages'),
    path('packages/ingestion',   ingestion, name='ingestion'),
    path('packages/<slug:name>', package,   name='package'),

]