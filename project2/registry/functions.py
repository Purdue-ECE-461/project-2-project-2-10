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

