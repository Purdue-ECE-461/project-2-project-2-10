import time
import json
import requests

def reset_database(url):
    url      = url + "reset"
    response = requests.delete(url)

    print("DELETE reset status code: ", response.status_code)

def create_package(url, packagePath, packageName, id="0"):
    url = url + "package"

    with open(packagePath, "rb") as file:
        content = file.read().decode("Cp437")

    body = {
        "metadata": json.dumps({
            "Name": packageName,
            "Version": "1.0." + id,
            "ID": packageName + id,
        }), 
        "data": json.dumps({
            "Content": content,
            "JSProgram": "return 0;"
        })
    }

    response = requests.post(url, data=body)

    print("POST " + packageName + " status code: ", response.status_code)

def get_packages(url):
    url      = url + "package"
    response = requests.get(url)

    packageIds = []

    print("GET packages status code: ", response.status_code)
    for package in json.loads(response.content.decode("utf-8"))["packages"]:
        print("\t", package)
        packageIds.append(package)

    return packageIds

def get_package(url, id):
    url      = url + "package/" + id
    response = requests.get(url)

    print("GET package id:" + id + " status code: ", response.status_code)
    print("\t", json.loads(response.content.decode("utf-8"))["metadata"])

def update_package(url, package, newPackagePath):
    with open(newPackagePath, "rb") as file:
        content = file.read().decode("Cp437")

    url  = url + "package/" + package["ID"]
    body = json.dumps({
        "metadata": json.dumps({
            "Name": package["Name"],
            "Version": "1.0.0",
            "ID": package["ID"],
        }), 
        "data": json.dumps({
            "Content": content,
        })
    })

    response = requests.put(url, data=body)

    print("PUT package id:" + package["ID"] + " status code: ", response.status_code)

def delete_package(url, id):
    url      = url + "package/" + id
    response = requests.delete(url)

    print("DELETE package id:" + id + " status code: ", response.status_code)

def get_package_rating(url, id):
    url      = url + "package/" + id + "/rate"
    response = requests.get(url)

    print("GET package id:" + id + " rating status code: ", response.status_code)
    for subScores in json.loads(response.content.decode("utf-8")).items():
        print("\t", subScores[0], ":", subScores[1])

def get_package_by_name(url, name):
    url      = url + "package/byName/" + name
    response = requests.get(url)

    print("GET package name:" + name + " status code: ", response.status_code)
    for history in json.loads(response.content.decode("utf-8")):
        print("\t", history)

def delete_packages_by_name(url, name):
    url      = url + "package/byName/" + name
    response = requests.delete(url)

    print("DELETE package name:" + name + " status code: ", response.status_code)

def request_ingestion(url, githubUrl, packageName, id="0"):
    url = url + "package"

    body = {
        "metadata": json.dumps({
            "Name": packageName,
            "Version": "1.0." + id,
            "ID": packageName + id,
        }), 
        "data": json.dumps({
            "URL": githubUrl,
            "JSProgram": "return 0;"
        })
    }

    response = requests.post(url, data=body)

    print("POST (ingestion)" + packageName + " status code: ", response.status_code)


if __name__ == "__main__":
    # url = "https://symmetric-index-334318.uc.r.appspot.com/"
    url = "http://127.0.0.1:8000/"

    resetResponse = reset_database(url)

    create_package(url, "../zipped_folders/browserify-master.zip", "browserify-master")
    create_package(url, "../zipped_folders/cloudinary_npm-master.zip", "cloudinary_npm-master")
    create_package(url, "../zipped_folders/nodist-master.zip", "nodist-master")
    request_ingestion(url, "https://github.com/expressjs/express", "express-master")

    packages = get_packages(url)

    get_package(url, packages[0]["ID"])
    update_package(url, packages[0], "../zipped_folders/express-master.zip")
    delete_package(url, packages[1]["ID"])

    packages = get_packages(url)

    get_package_rating(url, packages[0]["ID"])

    create_package(url, "../zipped_folders/browserify-master.zip", "browserify-master", id="1")
    create_package(url, "../zipped_folders/browserify-master.zip", "browserify-master", id="2")
    create_package(url, "../zipped_folders/browserify-master.zip", "browserify-master", id="3")

    time.sleep(2)

    get_package_by_name(url, "browserify-master")

    delete_packages_by_name(url, "browserify-master")



