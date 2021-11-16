import json
import sys

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse

from .models import Package
from .functions import save_file, get_file_content, get_github_scores

@csrf_exempt
def reset(request):
    try:
        if request.method == "DELETE":
            for temp_pacakge in Package.objects.all():
                temp_pacakge.delete()

            return HttpResponse(status=200)

        return HttpResponse(status=404)

    except (Exception,):
        print(" [ERROR]", sys.exc_info())
        return HttpResponse(status=500)   

@csrf_exempt
def packages(request):
    try:
        # Endpoint for uploading a new package. Recieves a request that contains a zipped package
        # and metadata about that package. Calls save_file() to save the zipped package in
        # persistent data, and saves the package's metadata to a SQL database.

        if request.method == "POST":
            metadata = json.loads(request.POST["metadata"])
            data     = json.loads(request.POST["data"])

            zipped_file_content = data['Content']
            file_location      = save_file(metadata['Name'], zipped_file_content)

            packages_with_same_name_and_version = Package.objects.filter(
                name    = metadata["Name"],
                version = metadata["Version"]
            )
            packages_with_same_id = Package.objects.filter(
                package_id = metadata["ID"]
            )

            if packages_with_same_name_and_version.exists() or packages_with_same_id.exists():
                return HttpResponse(status=403)

            Package.objects.create(
                name       = metadata["Name"],
                package_id = metadata["ID"],
                version    = metadata["Version"],
                file_path  = file_location,
                github_url = data["URL"],
                js_program = data["JSProgram"]
            )

            return HttpResponse(status=201)

        # Endpoint for getting a paginated list of packages. Returns a list of packages (number
        # of packages determined by batchSize) and an integer that's used to determine the next
        # list of packages. This integer is sent by the client on their next call to indicate
        # that the client wants the next batch of packages.

        if request.method == "GET":
            batch_size = 2

            offset = request.GET.get('offset')
            if offset is None:
                offset = 0
            else:
                offset = int(offset)

            package_list = []
            for temp_package in Package.objects.all()[offset:offset + batch_size]:
                package_list.append(temp_package.to_dict())

            return JsonResponse({
                "packages": package_list,
                "nextOffset": offset + batch_size
            }, status=200)

        return HttpResponse(status=404)

    except (Exception,):
        print(" [ERROR]", sys.exc_info())
        return HttpResponse(status=500)

@csrf_exempt
def package(request, package_id=None):
    try:
        # Given a package's name, returns that package and it's metadata.

        if request.method == "GET":
            requested_package = Package.objects.get(package_id=package_id)
            file_content      = get_file_content(requested_package.file_path)
            return_data       = {
                "metadata": requested_package.to_dict(),
                "data": {
                    "Content":   file_content,
                    "URL":       requested_package.github_url,
                    "JSProgram": requested_package.js_program
                }
            }
            return JsonResponse(return_data, status=200)

        # Updates a package's data (including it's file content) based on the given values.
        # Only performs the update if the given id, name, and version match an existing
        # package.

        if request.method == "PUT":
            request_data = json.loads(request.body.decode("utf8"))
            metadata     = request_data["metadata"]
            data         = request_data["data"]

            updated_package = Package.objects.get(package_id=package_id)

            do_names_match    = metadata["Name"] == updated_package.name
            do_versions_match = metadata["Version"] == updated_package.version

            if not do_names_match or not do_versions_match:
                return HttpResponse(status=400)

            updated_package.github_url = data["URL"]
            updated_package.js_program = data["JSProgram"]
            updated_package.file_path  = save_file(metadata["Name"], data["Content"])
            updated_package.save()

            return HttpResponse(status=200)

        # Deletes a package from the database. TODO: delete corresponding package file from
        # file storage.

        if request.method == "DELETE":
            updated_package = Package.objects.get(package_id=package_id)
            updated_package.delete()

            return HttpResponse(status=200)

        return HttpResponse(status=404)

    except (Exception,):
        print(" [ERROR]", sys.exc_info())
        return HttpResponse(status=500)

@csrf_exempt
def rating(request, package_id=None):
    try:
        # Given a package name, gets the score and sub scores for that package (using its
        # github url). Returns a json containing the score and subscore.

        if request.method == "GET":
            rated_package  = Package.objects.get(package_id=package_id)
            sub_score_dict = get_github_scores(rated_package.github_url)

            return JsonResponse(sub_score_dict, status=200)

        return HttpResponse(status=404)

    except (Exception,):
        print(" [ERROR]", sys.exc_info())
        return HttpResponse(status=500)

@csrf_exempt
def by_name(request, name=None):
    try:
        if request.method == "DELETE":
            package_list = Package.objects.filter(name=name)
            for temp_package in package_list:
                temp_package.delete()

            return HttpResponse(status=200)

        return HttpResponse(status=404)

    except (Exception,):
        print(" [ERROR]", sys.exc_info())
        return HttpResponse(status=500)
