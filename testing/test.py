import requests
import json

if __name__ == "__main__":
    url      = "http://127.0.0.1:8000/"
    endpoint = url + "v1/package" 
    files    = { 'zipped_package': open('test.txt','r') }

    response = requests.post(
        endpoint,
        data = {
            'name': 'package'
        },
        files = files
    )

    print(response.status_code)