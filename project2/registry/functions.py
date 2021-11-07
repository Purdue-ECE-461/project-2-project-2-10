import os
import zipfile
import re

# THIS FUNCTION PROVIDES FUNCTIONALITY THAT WILL ONLY BE RUN IN DEVELOPMENT ENVIRONMENT. 
# Saves the given file to a location given by fileName.
 
def save_file(fileName, inMemoryFile):
    directoryPath = "/Users/johnbensen/Documents/ECE/ECE461/PROJECT_2/project-2-project-2-10/project2/temp_files/"
    filePath      = directoryPath + fileName

    with open(filePath, 'wb') as file:
        for chunk in inMemoryFile.chunks():
            file.write(chunk)

    return filePath

# THIS FUNCTION PROVIDES FUNCTIONALITY THAT WILL ONLY BE RUN IN DEVELOPMENT ENVIRONMENT. 
# Returns a file object for the given filePath. s

def get_file(filePath):
    return open(filePath, "rb")

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

def get_github_url_from_zipped_package(packagePath):
    with zipfile.ZipFile(packagePath) as zipped:
        packageJsonName = ""
        for name in zipped.namelist():
            if "package.json" in name:
                packageJsonName = name
                break

        mainLine           = b""
        inRepositoryObject = False
        with zipped.open(packageJsonName) as file:
            for line in file.readlines():
                if b"homepage" in line and b"github.com" in line:
                    mainLine = line
                    break

                elif b"repository" in line and b"{" not in line:
                    mainLine = line
                    break

                elif b"repository" in line:
                    inRepositoryObject = True

                elif inRepositoryObject and b"url" in line:
                    mainLine = line
                    break

    mainLineString = mainLine.decode("utf-8")

    if "github.com" not in mainLineString and "repository" in mainLineString:
        mainLineString = mainLineString.split("\"")[3]
        mainLineString = "https://github.com/" + mainLineString

    if "\"homepage\"" in mainLineString or "\"url\":" in mainLineString:
        mainLineString = mainLineString.split("\"")[3]

    githubUrl = mainLineString.split(".git")[0]

    return githubUrl

if __name__ == "__main__":
    packageDirectory = '/Users/johnbensen/Documents/ECE/ECE461/PROJECT_2/project-2-project-2-10/zipped_folders/'

    get_github_url_from_zipped_package(packageDirectory + "cloudinary_npm-master.zip")
    get_github_url_from_zipped_package(packageDirectory + "browserify-master.zip")
    get_github_url_from_zipped_package(packageDirectory + "express-master.zip")
    get_github_url_from_zipped_package(packageDirectory + "lodash-master.zip")
    get_github_url_from_zipped_package(packageDirectory + "nodist-master.zip")