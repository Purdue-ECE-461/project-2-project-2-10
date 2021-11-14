from django.urls import path

from .views import *

urlpatterns = [
    path('package',                     packages,   name='packages'),
    path('package/<slug:id>',           package,    name='package'),
    path('package/<slug:id>/rate',      rating,     name='rating'),
    path('package/byName/<slug:name>',  byName,     name="byName")

]