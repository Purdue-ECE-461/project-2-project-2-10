import json
import sys 
import os

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.core.files.storage import default_storage
from django.http import QueryDict

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
            metadata = json.loads(request.POST["metadata"])
            data     = json.loads(request.POST["data"])

            zippedFileContent = data['Content']
            fileLocation      = save_file(metadata['Name'], zippedFileContent)

            packagesWithNameVersion = Package.objects.filter(name=metadata["Name"], version=metadata["Version"])
            packagesWithId          = Package.objects.filter(packageId=metadata["ID"])
            if packagesWithNameVersion.exists() or packagesWithId.exists():
                return HttpResponse(status=403)

            Package.objects.create(
                name      = metadata["Name"],
                packageId = metadata["ID"],
                version   = metadata["Version"],
                filePath  = fileLocation,
                githubUrl = data["URL"],
                jsProgram = data["JSProgram"]
            )

            return HttpResponse(status=201)

        # Endpoint for getting a paginated list of packages. Returns a list of packages (number of packages
        # determined by batchSize) and an integer that's used to determine the next list of packages. This 
        # integer is sent by the client on their next call to indicate that the client wants the next batch
        # of packages. 

        if request.method == "GET":
            batchSize = 2

            offset = request.GET.get('offset')
            if offset == None:
                offset = 0
            else:
                offset = int(offset)

            packages = []
            for package in Package.objects.all()[offset:offset + batchSize]:
                packages.append(package.to_dict())
            
            return HttpResponse(json.dumps({
                "packages": packages,
                "nextOffset": offset + batchSize
            }), status=200)

    except:
        print(" [ERROR]", sys.exc_info())
        return HttpResponse(status=500)

@csrf_exempt
def package(request, id=None):
    try:
        # Given a package's name, returns that package and it's metadata.

        if request.method == "GET":
            package     = Package.objects.get(packageId=id)
            fileContent = get_file_content(package.filePath)
            returnData = {
                "metadata": package.to_dict(),
                "data": {
                    "Content":   fileContent,
                    "URL":       package.githubUrl,
                    "JSProgram": package.jsProgram
                }
            }          
            return HttpResponse(json.dumps(returnData), status=200)

        # Updates a package's data (including it's file content) based on the given values. Only
        # performs the update if the given id, name, and version match an existing package. 

        if request.method == "PUT":
            requestData = json.loads(request.body.decode("utf8"))
            metadata    = requestData["metadata"]
            data        = requestData["data"]

            package = Package.objects.get(packageId=id)

            if metadata["Name"] != package.name or metadata["Version"] != package.version:
                return HttpResponse(status=400)

            package.githubUrl = data["URL"]
            package.jsProgram = data["JSProgram"]
            package.filePath  = save_file(metadata["Name"], data["Content"])
            package.save()

            return HttpResponse(status=200)

        # Deletes a package from the database. TODO: delete corresponding package file from file
        # storage. 

        if request.method == "DELETE":
            package = Package.objects.get(packageId=id)
            package.delete()

            return HttpResponse(status=200)

    except:
        print(" [ERROR]", sys.exc_info())
        return HttpResponse(status=500)

@csrf_exempt
def rating(request, id=None):
    try:
        # Given a package name, gets the score and sub scores for that package (using its github
        # url). Returns a json containing the score and subscore. 

        if request.method == "GET":
            package      = Package.objects.get(packageId=id)
            subScoreDict = get_github_scores(package.githubUrl)

            return HttpResponse(json.dumps(subScoreDict), status=200)

    except:
        print(" [ERROR]", sys.exc_info())
        return HttpResponse(status=500)

@csrf_exempt
def byName(request, name=None):
    try:
        if request.method == "DELETE":
            packages = Package.objects.filter(name=name)
            for package in packages:
                package.delete()

            return HttpResponse(status=200)

    except:
        print(" [ERROR]", sys.exc_info())
        return HttpResponse(status=500)


