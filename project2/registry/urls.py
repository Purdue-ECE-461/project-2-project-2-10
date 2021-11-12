from django.urls import path

from .views import *

urlpatterns = [
    path('package',                  packages,  name='packages'),
    path('package/<slug:name>',      package,   name='package'),
    path('package/<slug:name>/rate', rating,    name='rating'),

]