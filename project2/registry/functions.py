import json
from datetime import datetime

from google.cloud import storage
from google.cloud import logging as gcloud_logging

from .project1 import main as project1

# Saves the given file in stored and creates a new entity in the database that contains
# the package's metadata.

def save_file(package_name, zipped_file_content):
    storage_client = storage.Client()
    bucket         = storage_client.bucket("bucket-461-packages")
    blob           = bucket.blob(package_name)

    blob.upload_from_string(zipped_file_content)

    return package_name

# THIS FUNCTION PROVIDES FUNCTIONALITY THAT WILL ONLY BE RUN IN DEVELOPMENT ENVIRONMENT.
# Returns a file object for the given filePath. Zipped files are encoded in "Cp437", so
# it has to be decoded in "Cp437" in order to be added to the json object.

def get_file_content(package_name):
    storage_client = storage.Client()
    bucket         = storage_client.bucket("bucket-461-packages")
    blob           = bucket.blob(package_name)

    return blob.download_as_string().decode("Cp437")

# Given a github url for a npm package, uses the functionality provided by project 1 to
# calculate and return the package's overall score and a list of its subscores.

def get_github_scores(github_url):
    score_dict = project1.gitOrNpm([github_url])
    scores     = list(score_dict.values())[0]
    sub_scores = scores[1:]

    sub_score_names = ["RampUp", "Correctness", "BusFactor", "ResponsiveMaintainer", "LicenseScore"]
    sub_score_dict  = {}
    for i, name in enumerate(sub_score_names):
        sub_score_dict[name] = sub_scores[i]

    return sub_score_dict

class PackageLogger:
    def __init__(self):
        self.logger_name    = "PACKAGE_HISTORY"
        self.logging_client = gcloud_logging.Client()
        self.logging_client.setup_logging()
        self.logger = self.logging_client.logger(self.logger_name)

    def delete_logs(self):
        self.logger.delete()

    def get_package_name_history(self, package_name):
        package_history = []

        filter_string = "logName:projects/micro-arcadia-332215/logs/" + self.logger_name
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
