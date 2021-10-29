import json

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.core.files.storage import default_storage

from .models import *
from .functions import *

@csrf_exempt
def package(request):
    # Endpoint for uploading a new package. Recieves a request that contains a zipped pacakge and
    # metadata about that package. Calls save_file() to save the zipped package in persistent data,
    # and saves the package's metadata to a SQL database. 
    
    if request.method == "POST":
        inMemoryFile = request.FILES['zipped_package']
        filePath     = save_file(inMemoryFile.name, inMemoryFile)

        package = Package.objects.create(
            name     = request.POST['name'],
            filePath = filePath
        )
        return HttpResponse(status=201)