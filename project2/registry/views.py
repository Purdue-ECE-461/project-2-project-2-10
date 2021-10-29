import json
import sys 
import os

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.core.files.storage import default_storage

from .models import *
from .functions import *

@csrf_exempt
def packages(request):
    try:
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

        # Endpoint for getting a paginated list of packages. No functionality is provided for this endpoint
        # as of right now. 

        if request.method == "GET":
            pass

    except:
        print(" [ERROR]", sys.exc_info())
        return HttpResponse(status=500)

@csrf_exempt
def package(request, name):
    try:
        # Given a package's name, returns that package. WE ARE USING .txt FILES FOR DEVELOPMENT PURPOSES,
        # THE "content_type" SHOULD CHANGE FOR ZIPPED FILES.

        if request.method == "GET":
            package = Package.objects.get(name=name)
            file    = get_file(package.filePath)

            return HttpResponse(file, content_type='text/plain', status=200)
    except:
        print(" [ERROR]", sys.exc_info())
        return HttpResponse(status=500)


