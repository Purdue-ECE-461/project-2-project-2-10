import json
import sys 
import os

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.core.files.storage import default_storage

from .models import *
from .functions import *
from .project1 import main as project1

@csrf_exempt
def packages(request):
    try:
        # Endpoint for uploading a new package. Recieves a request that contains a zipped pacakge and
        # metadata about that package. Calls save_file() to save the zipped package in persistent data,
        # and saves the package's metadata to a SQL database. 
        
        if request.method == "POST":
            inMemoryFile = request.FILES['zipped_package']
            save_file(request.POST['name'], inMemoryFile)

            return HttpResponse(status=201)

        # Endpoint for getting a paginated list of packages. Returns a list of packages (number of packages
        # determined by batchSize) and an integer that's used to determine the next list of packages. This 
        # integer is sent by the client on their next call to indicate that the client wants the next batch
        # of packages. 

        if request.method == "GET":
            batchSize = 2

            index = request.GET.get('index')
            if index == None:
                index = 0
            else:
                index = int(index)

            packages = []
            for package in Package.objects.all()[index:index + batchSize]:
                packages.append(package.to_dict())
            
            return HttpResponse(json.dumps({
                "packages": packages,
                "nextIndex": index + batchSize
            }), status=200)

    except:
        print(" [ERROR]", sys.exc_info())
        return HttpResponse(status=500)

@csrf_exempt
def package(request, name):
    try:
        # Given a package's name, returns that package. Only returns the zipped file. 

        if request.method == "GET":
            package = Package.objects.get(name=name)
            file    = get_file(package.filePath)

            return HttpResponse(file, status=200)
    except:
        print(" [ERROR]", sys.exc_info())
        return HttpResponse(status=500)

@csrf_exempt
def ingestion(request):
    try:
        inMemoryFile = request.FILES['zipped_package']
        githubUrl    = get_github_url_from_zipped_package(inMemoryFile)
        packageName  = request.POST['name']
        _, subScores = get_github_scores(githubUrl)

        areScoresGoodEnough = True
        for subScore in subScores:
            if subScore < .5:
                areScoresGoodEnough = False 

        if areScoresGoodEnough:
            save_file(packageName, inMemoryFile)

        return HttpResponse(json.dumps({"isFileSaved": areScoresGoodEnough}), status=200)

    except:
        print(" [ERROR]", sys.exc_info())
        return HttpResponse(status=500)