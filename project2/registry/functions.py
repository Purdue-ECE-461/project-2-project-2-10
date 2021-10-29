import os

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


