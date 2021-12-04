import json
import sys

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse

from .models import Package
from .functions import *

package_logger = PackageLogger()

@csrf_exempt
def reset(request):
    try:
        if request.method == "DELETE":
            for temp_pacakge in Package.objects.all():
                temp_pacakge.delete()
            package_logger.delete_logs()

            return HttpResponse(status=200)

        return HttpResponse(status=404)

    except (Exception,):
        print(" [ERROR]", sys.exc_info())
        return HttpResponse(status=500)

@csrf_exempt
def packages(request):
    try:
        # Endpoint for uploading a new package. Recieves metadata about the package and 2 possible
        # bodies: a github url or the package content. If the githhub url is given, then checks if
        # the package is "ingestible" (all subscores > .5). If it is, then downloads the package
        # content from github and creates a new package. If the package content is given, then
        # searchs through the package content to find its github url, and creates a new package.

        if request.method == "POST":
            metadata = json.loads(request.POST["metadata"])
            data     = json.loads(request.POST["data"])

            if check_if_package_exists(metadata["Name"], metadata["Version"], metadata["ID"]):
                return HttpResponse(status=403)

            github_url      = None
            package_content = None

            if "URL" in data:
                if check_if_ingestible(data["URL"]):
                    github_url      = data["URL"]
                    package_content = get_content_from_url(github_url)
                else:
                    return HttpResponse(status=400)
            else:
                package_content = data['Content'].encode("Cp437")
                github_url      = get_github_url_from_zipped_package(package_content)

            file_location = save_file(metadata['Name'], package_content)

            created_package = Package.objects.create(
                name       = metadata["Name"],
                package_id = metadata["ID"],
                version    = metadata["Version"],
                file_path  = file_location,
                github_url = github_url,
                js_program = data["JSProgram"]
            )

            package_logger.log_create(created_package, None)

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
        # Given a package's name, returns that package and it's metadata. If the package is
        # "secret", then runs a js program on the package's content and returns the result.

        if request.method == "GET":
            requested_package = Package.objects.get(package_id=package_id)
            return_value      = None

            if requested_package.is_secret and run_js_program(requested_package, "downloader") != 0:
                return_value = HttpResponse(status=400)

            else:
                file_content = get_file_content(requested_package.file_path)
                return_data  = {
                    "metadata": requested_package.to_dict(),
                    "data": {
                        "Content":   file_content,
                        "URL":       requested_package.github_url,
                        "JSProgram": requested_package.js_program
                    }
                }
                package_logger.log_download(requested_package, None)
                return_value = JsonResponse(return_data, status=200)

            return return_value

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

            package_logger.log_update(updated_package, None)

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

            package_logger.log_rate(rated_package, None)

            return JsonResponse(sub_score_dict, status=200)

        return HttpResponse(status=404)

    except (Exception,):
        print(" [ERROR]", sys.exc_info())
        return HttpResponse(status=500)

@csrf_exempt
def by_name(request, name=None):
    try:
        if request.method == "GET":
            package_history = package_logger.get_package_name_history(name)
            return JsonResponse(package_history, safe=False)

        if request.method == "DELETE":
            package_list = Package.objects.filter(name=name)
            for temp_package in package_list:
                temp_package.delete()

            return HttpResponse(status=200)

        return HttpResponse(status=404)

    except (Exception,):
        print(" [ERROR]", sys.exc_info())
        return HttpResponse(status=500)
