from django.urls import path

from .views import *

urlpatterns = [
    path('package',                      packages,    name='packages'),
    path('package/<slug:id>',            package,     name='package'),
    path('package/<slug:id>/rate',       rating,      name='rating'),
    path('package/by_name/<slug:name>',  by_name,     name="by_name")

]