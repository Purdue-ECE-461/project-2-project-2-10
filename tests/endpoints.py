import json
import requests

def create_package(url):
    url = url + "package"

    with open("../zipped_folders/browserify-master.zip", "rb") as file:
        content = file.read().decode("Cp437")

    body = {
        "metadata": json.dumps({
            "Name": "browserify",
            "Version": "1.0.0",
            "ID": "1",
        }), 
        "data": json.dumps({
            "Content": content,
            "JSProgram": "return 0;"
        })
    }

    response = requests.post(url, data=body)

    print("POST package status code: ", response.status_code)

if __name__ == "__main__":
    url = "http://127.0.0.1:8000/"

    create_package(url)
