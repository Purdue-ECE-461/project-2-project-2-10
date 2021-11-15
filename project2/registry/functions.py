from .project1 import main as project1

# THIS FUNCTION PROVIDES FUNCTIONALITY THAT WILL ONLY BE RUN IN DEVELOPMENT ENVIRONMENT.
# Saves the given file in stored and creates a new entity in the database that contains
# the package's metadata.

def save_file(package_name, zipped_file_content):
    directory_path = "temp_files/"
    file_path      = directory_path + package_name

    with open(file_path, 'wb') as file:
        file.write(zipped_file_content.encode("Cp437"))

    return file_path

# THIS FUNCTION PROVIDES FUNCTIONALITY THAT WILL ONLY BE RUN IN DEVELOPMENT ENVIRONMENT.
# Returns a file object for the given filePath. Zipped files are encoded in "Cp437", so
# it has to be decoded in "Cp437" in order to be added to the json object.

def get_file_content(file_path):
    with open(file_path, "rb") as file:
        return file.read().decode("Cp437")

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
