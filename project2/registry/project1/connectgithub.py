import requests
import re
import urllib.parse
import base64
import json
from .readEnvironment import *

# GITHUB_TOKEN = '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'
headers = {'Authorization': 'token ' + GITHUB_TOKEN}
# logFile_ptr = open(LOG_FILE, "w")
# # logFile_ptr = open("logFile.txt", "w")
# LOG_LEVEL = "1"


def getUrl(url):
    parsed = urllib.parse.urlsplit(url).path
    count = 0
    user = ""
    repo = ""

    for i in parsed:
        if i == "/":
            count += 1
        if i != "/" and count == 1:
            user += i
        if i != "/" and count == 2:
            repo += i

    base_url = f"https://api.github.com/repos/{user}/{repo}"

    if LOG_LEVEL == "1" or LOG_LEVEL == "2":
        message = "Running getUrl\n"
        # logFile_ptr.write(message)

    return base_url


def get_contributors(baseURL):
    baseURL = baseURL + "/contributors"
    # print(baseURL)
    response = requests.get(baseURL, headers=headers)
    data = response.json()

    if LOG_LEVEL == "1" or LOG_LEVEL == "2":
        message = "Running get_contributors\n"
        # logFile_ptr.write(message)

    return len(data)


def get_assignees(baseURL):
    baseURL = baseURL + "/assignees"
    # print(baseURL)
    response = requests.get(baseURL, headers=headers)
    data = response.json()

    if LOG_LEVEL == "1" or LOG_LEVEL == "2":
        message = "Running get_assignees\n"
        # logFile_ptr.write(message)

    return len(data)


def get_releases(baseURL):
    baseURL = baseURL + "/releases"
    # print(baseURL)
    response = requests.get(baseURL, headers=headers)
    data = response.json()

    if LOG_LEVEL == "1" or LOG_LEVEL == "2":
        message = "Running get_releases\n"
        # logFile_ptr.write(message)

    return len(data)


def get_commits(baseURL):
    baseURL = baseURL + "/commits"
    # print(baseURL)
    response = requests.get(baseURL, headers=headers)
    data = response.json()
    if LOG_LEVEL == "1" or LOG_LEVEL == "2":
        message = "Running get_commits\n"
        # logFile_ptr.write(message)

    return len(data)


def get_version(packageJSON):
    if LOG_LEVEL == "1":
        message = "Getting API Version\n"
        # logFile_ptr.write(message)
    if LOG_LEVEL == "2":
        message = "Getting API Version using package.json file\n"
        # logFile_ptr.write(message)
    return packageJSON['version']


def get_dependencies(packageJSON):
    if LOG_LEVEL == "1":
        message = "Getting Dependencies\n"
        # logFile_ptr.write(message)
    if LOG_LEVEL == "2":
        message = "Getting Dependencies using package.json file\n"
        # logFile_ptr.write(message)
    return len(packageJSON['dependencies'])


def get_devDependencies(packageJSON):
    if LOG_LEVEL == "1":
        message = "Getting devDependencies\n"
        # logFile_ptr.write(message)
    if LOG_LEVEL == "2":
        message = "Getting devDependencies using package.json file\n"
        # logFile_ptr.write(message)
    return len(packageJSON['devDependencies'])


def get_license(packageJSON):

    if 'license' in packageJSON:
        output = packageJSON['license']
    else:
        output = {}
    if LOG_LEVEL == "1":
        message = "Getting Licenses\n"
        # logFile_ptr.write(message)
    if LOG_LEVEL == "2":
        message = "Getting Licenses using package.json file\n"
        # logFile_ptr.write(message)
    return output


def getJSONPackage(baseURL):
    baseURL  = baseURL + "/contents/package.json"
    response = requests.get(baseURL, headers=headers)
    data     = response.json()
    if 'content' in data:
        base64_message = base64.b64decode(data['content'])
        output         = base64_message.decode()
        output         = json.loads(output)
        # print(type(output))
    else:
        output = {}

    if LOG_LEVEL == "1":
        message = "Running getJSONPackage\n"
        # logFile_ptr.write(message)
    if LOG_LEVEL == "2":
        message = "Running getJSONPackage and getting package.json file from the github repo for the API\n "
        # logFile_ptr.write(message)

    return output


def scoreBusFactor(baseURL):
    score = get_assignees(baseURL) / (get_contributors(baseURL) + 1)

    if score > 1:
        score = 1
    elif score < 0:
        score = 0

    if LOG_LEVEL == "1":
        message = "Running scoreBusFactor\n"
        # logFile_ptr.write(message)
    if LOG_LEVEL == "2":
        message = "Running scoreBusFactor and getting BusFactor score from scoreBusFactor function " \
                  "by running get_assignees and get_contributors for the API \n"
        # logFile_ptr.write(message)

    return score


def scoreResponsiveness(baseURL):
    score = get_releases(baseURL) / (get_commits(baseURL) + 1)

    if score > 1:
        score = 1
    elif score < 0:
        score = 0

    if LOG_LEVEL == "1":
        message = "Running scoreResponsiveness\n"
        # logFile_ptr.write(message)
    if LOG_LEVEL == "2":
        message = "Running scoreResponsiveness and getting RampUp score from scoreResponsiveness function " \
                  "using get_releases and get_commits for the API\n"
        # logFile_ptr.write(message)

    return score


def scoreCorrectness(packageJSON):
    version = get_version(packageJSON)
    first_dot = version.find(".")
    second_dot = version.rfind(".")
    number = version[second_dot + 1::]
    # major = int(float(version[0:first_dot]))
    # minor = int(float(version[first_dot + 1:second_dot]))
    # patch = int(float(version[second_dot + 1::]))

    firstChar = len(version)
    # print(number)
    x = re.search("[^\d]", number)
    # print(x)
    if x:
        firstChar = version.find(x.group())

    major = int(float(version[0:first_dot]))
    minor = int(float(version[first_dot + 1:second_dot]))
    patch = int(float(version[second_dot + 1:firstChar]))
    # print(patch)

    denominator = major if major != 0 else 1
    denominator *= minor if minor != 0 else 1
    denominator *= patch if patch != 0 else 1
    if denominator == 0:
        denominator = 1
    score = 1 - ((major + minor + patch) / denominator)

    if score > 1:
        score = 1
    elif score < 0:
        score = 0

    if LOG_LEVEL == "1":
        message = "Running scoreCorrectness\n"
        # logFile_ptr.write(message)
    if LOG_LEVEL == "2":
        message = "Running scoreCorrectness and calculating correctness score from scoreCorrectness function using " \
                  "the current version " \
                  "of the API and comparing how many versions have been made for the same release\n "
        # logFile_ptr.write(message)

    return score


def scoreRampup(packageJSON):
    if 'dependencies' in packageJSON and 'devDependencies' in packageJSON:
        score = get_devDependencies(packageJSON) / (get_dependencies(packageJSON) + 1)
        if score > 1:
            score = 1
        elif score < 0:
            score = 0
    else:
        score = 0

    if LOG_LEVEL == "1":
        message = "Running scoreRampup\n"
        # logFile_ptr.write(message)
    if LOG_LEVEL == "2":
        message = "Running scoreRampup and getting RampUp score from scoreRampup function using devDependencies and " \
                  "dependencies of the API \n"
        # logFile_ptr.write(message)

    return score


def scoreLicCompat(packageJSON):
    compatible_licenses = [
        "Public Domain",
        "MIT",
        "X11",
        "BSD-new",
        "Apache 2.0",
        "LGPLv2.1",
        "LGPLv2.1+",
        "LGPLv3",
        "LGPLv3+",
    ]
    lic = get_license(packageJSON)
    score = 0
    for i in compatible_licenses:
        if score:
            break
        score = 0 if re.search(i, lic) is None else 1

    if LOG_LEVEL == "1":
        message = "Getting License compatibility from scoreLicCompat function\n"
        # logFile_ptr.write(message)
    if LOG_LEVEL == "2":
        message = "Comparing a set of pre-chosen licenses to compare with the the license type of current API\n"
        # logFile_ptr.write(message)

    return score


def cumulativeScore(baseURL, packageJSON):
    score = []
    if len(packageJSON) == 0:
        x = (5 * scoreBusFactor(baseURL) + 4 * scoreResponsiveness(baseURL)) / 15
        score.append(round(x, 2))
    else:
        x = (5 * scoreBusFactor(baseURL) + 4 * scoreResponsiveness(baseURL) + 3 * scoreRampup(
            packageJSON) + 2 * scoreCorrectness(packageJSON) + scoreLicCompat(packageJSON)) / 15
        score.append(round(x, 2))

    if len(packageJSON) != 0:
        score.append(round(scoreRampup(packageJSON), 2))
    else:
        score.append(0)
    if len(packageJSON) != 0:
        score.append(round(scoreCorrectness(packageJSON), 2))
    else:
        score.append(0)

    score.append(round(scoreBusFactor(baseURL), 2))
    score.append(round(scoreResponsiveness(baseURL), 2))

    if len(packageJSON) != 0:
        score.append(round(scoreLicCompat(packageJSON), 2))
    else:
        score.append(0)

    return score


def scoreGithub(url):
    baseurl = getUrl(url)
    packagejson = getJSONPackage(baseurl)
    totalScore = cumulativeScore(baseurl, packagejson)
    if LOG_LEVEL == "1":
        message = f"Scoring the API accessed by the Github URl:{url}\n"
        # logFile_ptr.write(message)
    if LOG_LEVEL == "2":
        message = f"Scoring the API accessed by the Github URl:{url}, using urllib.parse package to break down the " \
                  f"url and base64 package to convert the package.json file info into a string\n"
        # logFile_ptr.write(message)
    return totalScore


# if __name__ == "__main__":
#     requestCount = 8
#     # scores = scoreGithub("https://github.com/lodash/lodash")
#     # scores = scoreGithub("https://github.com/nullivex/nodist")
#     # logFile_ptr = open("LOG_FILE.txt", "w")
#     # scores = scoreGithub("https://github.com/cloudinary/cloudinary_npm")
#     scores = scoreGithub("https://github.com/jquery/jquery")
#     # logFile_ptr.close()
#     # print(LOG_LEVEL)
#     # print(LOG_FILE)
#     # print(type(GITHUB_TOKEN))
#     print(scores)
#     print(f"Number of JSON Request Made = {requestCount}")
