import os

from django.core.files.storage import default_storage

# THIS FUNCTION PROVIDES FUNCTIONALITY THAT WILL ONLY BE RUN IN DEVELOPMENT ENVIRONMENT. 
# Saves the given file to a location given by fileName.
 
def save_file(fileName, inMemoryFile):
    directoryPath = "/Users/johnbensen/Documents/ECE/ECE461/PROJECT_2/project2/temp_files/"
    filePath      = directoryPath + fileName

    with default_storage.open(filePath, 'wb+') as destination:
        for chunk in inMemoryFile.chunks():
            destination.write(chunk)

    return filePath