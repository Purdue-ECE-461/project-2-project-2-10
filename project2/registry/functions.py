import os
import zipfile
import re

from .project1 import main as project1
from .models import *

# THIS FUNCTION PROVIDES FUNCTIONALITY THAT WILL ONLY BE RUN IN DEVELOPMENT ENVIRONMENT. 
# Saves the given file in stored and creates a new entity in the database that contains
# the package's metadata. 
 
def save_file(packageName, zippedFileContent):
    directoryPath = "temp_files/"
    filePath      = directoryPath + packageName

    with open(filePath, 'w') as file:
        file.write(zippedFileContent)

    return filePath

# THIS FUNCTION PROVIDES FUNCTIONALITY THAT WILL ONLY BE RUN IN DEVELOPMENT ENVIRONMENT. 
# Returns a file object for the given filePath. Zipped files are encoded in "Cp437", so 
# it has to be decoded in "Cp437" in order to be added to the json object. 

def get_file_content(filePath):
    with open(filePath, "rb") as file:
        return file.read().decode("Cp437")

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

def get_github_url_from_zipped_package(file):
    with zipfile.ZipFile(file) as zipped:
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

# Given a github url for a npm package, uses the functionality provided by project 1 to
# calculate and return the package's overall score and a list of its subscores. 

def get_github_scores(githubUrl):
    scoreDict = project1.gitOrNpm([githubUrl])
    scores    = list(scoreDict.values())[0]
    mainScore = scores[0]
    subScores = scores[1:]

    subScoreNames = ["RampUp", "Correctness", "BusFactor", "ResponsiveMaintainer", "LicenseScore"]
    subScoreDict  = {}
    for i in range(len(subScoreNames)):
        subScoreDict[subScoreNames[i]] = subScores[i]

    return subScoreDict

# def

