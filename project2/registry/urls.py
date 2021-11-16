from django.urls import path

from .views import packages, package, rating, by_name, reset

urlpatterns = [
    path('reset',                           reset,       name='reset'),
    path('package',                         packages,    name='packages'),
    path('package/<slug:package_id>',       package,     name='package'),
    path('package/<slug:package_id>/rate',  rating,      name='rating'),
    path('package/by_name/<slug:name>',     by_name,     name="by_name")
]
