import json
import zipfile
import io
from datetime import datetime

import requests
import js2py

from google.cloud import storage
from google.cloud import logging as gcloud_logging

from .project1 import main as project1

from .models import Package

def check_if_package_exists(name, version, package_id):
    # A package "already exists" if there is a package with the same name and version or
    # if there is a package witht the same id. If either of these scenarios are met, then
    # returns True. Otherwise returns false.

    packages_with_same_name_and_version = Package.objects.filter(
        name    = name,
        version = version
    )
    packages_with_same_id = Package.objects.filter(
        package_id = package_id
    )
    return packages_with_same_name_and_version.exists() or packages_with_same_id.exists()

def save_file(package_name, zipped_file_content):
    # Saves the given file in stored and creates a new entity in the database that contains
    # the package's metadata.

    storage_client = storage.Client()
    bucket         = storage_client.bucket("project-2-10")
    blob           = bucket.blob(package_name)

    blob.upload_from_string(zipped_file_content)

    return package_name

def get_file_content(package_name):
    # Returns the file associated with the given package_name.

    storage_client = storage.Client()
    bucket         = storage_client.bucket("project-2-10")
    blob           = bucket.blob(package_name)

    return blob.download_as_string().decode("Cp437")

def check_if_ingestible(github_url):
    # A package is "ingestible" if all of its subscores are greater than .5.

    sub_score_dict = get_github_scores(github_url)

    is_ingestible = True
    for sub_score in sub_score_dict.values():
        if sub_score < .5:
            is_ingestible = False

    return is_ingestible

def get_github_url_from_zipped_package(package_content):
    # This function searches through a zipped packages "package.json" file to look for a github
    # url. This url can be stored in multiple ways, include:
    #   "repository": "[repository name]"
    #   "homepage":   "https://github.com/[repository name]"
    #   "repository": {
    #       "type": "git"
    #       "url":  "https://github.com/[repository name]"
    #   }
    # It is also possible that there is not github url in the package.json file. The way in which
    # the url is stored is not known in advance, so all of these possibilities have to be checked
    # for.

    with zipfile.ZipFile(io.BytesIO(package_content)) as zipped:
        package_json_name = ""
        for name in zipped.namelist():
            if "package.json" in name:
                package_json_name = name
                break

        main_line            = b""
        in_repository_object = False
        with zipped.open(package_json_name) as file:
            for line in file.readlines():
                if b"homepage" in line and b"github.com" in line:
                    main_line = line
                    break

                if b"repository" in line and b"{" not in line:
                    main_line = line
                    break

                if b"repository" in line:
                    in_repository_object = True

                if in_repository_object and b"url" in line:
                    main_line = line
                    break

    main_line_string = main_line.decode("utf-8")

    if "github.com" not in main_line_string and "repository" in main_line_string:
        main_line_string = main_line_string.split("\"")[3]
        main_line_string = "https://github.com/" + main_line_string

    if "\"homepage\"" in main_line_string or "\"url\":" in main_line_string:
        main_line_string = main_line_string.split("\"")[3]

    github_url = main_line_string.split(".git")[0]

    return github_url

def get_content_from_url(github_url):
    # Downloads a package's content directly from github.

    response = requests.get(github_url + "/archive/master.zip")
    return response.content

def get_github_scores(github_url):
    # Given a github url for a npm package, uses the functionality provided by project 1 to
    # calculate and return the package's overall score and a list of its sub_scores.

    score_dict = project1.gitOrNpm([github_url])
    scores     = list(score_dict.values())[0]
    sub_scores = scores[1:]

    sub_score_names = [
        "RampUp",
        "Correctness",
        "BusFactor",
        "ResponsiveMaintainer",
        "LicenseScore",
        "FractionPinned"
    ]
    sub_score_dict  = {}
    for i, name in enumerate(sub_score_names):
        sub_score_dict[name] = sub_scores[i]

    return sub_score_dict

def run_js_program(package, downloader):
    # Given a package and the person trying to download the package, runs a javascript program.
    # The javascript program is stored in the package's js_program feild. Returns the program's
    # output.

    module_name         = package.name
    module_version      = package.version
    uploader_username   = "none"
    downloader_username = downloader
    zip_file            = get_file_content(package.file_path)

    js_program = js2py.eval_js(f"""
        function f(MODULE_NAME, MODULE_VERSION, UPLOADER_USERNAME, DOWNLOADER_USERNAME, ZIP_FILE) {{
            {package.js_program}
        }}
    """)

    return js_program(module_name, module_version, uploader_username, downloader_username, zip_file)

class PackageLogger:
    def __init__(self):
        self.logger_name    = "PACKAGE_HISTORY"
        self.logging_client = gcloud_logging.Client()
        self.logging_client.setup_logging()
        self.logger = self.logging_client.logger(self.logger_name)

    def delete_logs(self):
        try:
            self.logger.delete()
        except (Exception,):
            pass

    def get_package_name_history(self, package_name):
        package_history = []

        filter_string = "logName:projects/symmetric-index-334318/logs/" + self.logger_name
        for entry in self.logging_client.list_entries(filter_=filter_string):
            payload = entry.payload
            if json.loads(payload["PackageMetadata"])["Name"] == package_name:
                package_history.append(payload)

        return package_history

    def log_download(self, package, user):
        self.__log_action(package, user, "DOWNLOAD")

    def log_update(self, package, user):
        self.__log_action(package, user, "UPDATE")

    def log_rate(self, package, user):
        self.__log_action(package, user, "RATE")

    def log_create(self, package, user):
        self.__log_action(package, user, "CREATE")

    def __log_action(self, package, user, action):
        log_body = {
            "User": str(user),
            "Date": str(datetime.today()),
            "PackageMetadata": json.dumps(
                package.to_dict()
            ),
            "Action": action
        }

        self.logger.log_struct(log_body)
