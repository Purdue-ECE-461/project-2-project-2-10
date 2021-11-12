import json

from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from .models import *
from .functions import *

class PackageTest(TestCase):
    def setUp(self):
        self.client = Client()

    # Tests to see if a zipped package is uploaded successfully and that the correct meta data
    # is stored. 
    def test_upload_package(self):
        packageName    = "UNIT_TEST"
        packageVersion = "1.0.0"
        packageID      = "UNIT_TEST_ID"
        packageURL     = "github.com/fake/url/path"
        jsProgram      = "if (process.argv.length === 7) {\nconsole.log('Success')\nprocess.exit(0)\n} else {\nconsole.log('Failed')\nprocess.exit(1)\n}\n"
        fakeContent    = "fake content data"

        packagePath  = "../zipped_folders/cloudinary_npm-master.zip"
        # originalFile = open(packagePath, "rb")

        response = self.client.post(
            reverse('packages'), 
            data = {
                "metadata": json.dumps({
                    "Name": packageName,
                    "Version": packageVersion,
                    "ID": packageID
                }),
                "data": json.dumps({
                    "Content": fakeContent,
                    "URL": packageURL,
                    "JSProgram": jsProgram
                })
            }
        )

        package = Package.objects.all()[0]
        with open(package.filePath, "r") as savedFile:
            self.assertEqual(savedFile.read(), fakeContent)

        self.assertEqual(response.status_code, 201)

    # Test to see if a package is able to be downloaded from the server. 
    def test_get_package(self):
        packageName    = "UNIT_TEST"
        packageVersion = "1.0.0"
        packageID      = "UNIT_TEST_ID"
        packageURL     = "github.com/fake/url/path"
        jsProgram      = "if (process.argv.length === 7) {\nconsole.log('Success')\nprocess.exit(0)\n} else {\nconsole.log('Failed')\nprocess.exit(1)\n}\n"
        packagePath    = "../project2/temp_files/cloudinary_npm-master.zip"

        Package.objects.create(
            name      = packageName,
            packageId = packageID,
            version   = packageVersion,
            githubUrl = packageURL,
            jsProgram = jsProgram,
            filePath  = packagePath
        )

        response = self.client.get(
            reverse('package', kwargs={'name': packageName})
        )
        responseContent = json.loads(response.content)

        with open(packagePath, "rb") as file:
            self.assertEqual(file.read(), responseContent["data"]["Content"].encode("Cp437"))

        self.assertEqual(responseContent["data"]["URL"], packageURL)
        self.assertEqual(responseContent["data"]["JSProgram"], jsProgram)
        self.assertEqual(responseContent["metadata"]["Name"], packageName)
        self.assertEqual(responseContent["metadata"]["Version"], packageVersion)
        self.assertEqual(responseContent["metadata"]["ID"], packageID)

    # Tests the pagination endpoint. Asks for a list of packages from the server, checks to see
    # if only two packages are returned at a time. Asks for a list of packages twice to see if 
    # a different list of packages are returned each time. 
    def test_get_paginated_list(self):
        package1 = Package.objects.create(
            name     = "browserify",
            filePath = "../zipped_folders/browserify-master.zip"
        )
        package2 = Package.objects.create(
            name     = "cloudinary",
            filePath = "project-2-project-2-10/zipped_folders/cloudinary_npm-master.zip"
        )
        package3 = Package.objects.create(
            name     = "express",
            filePath = "../zipped_folders/express-master.zip"
        )
        package4 = Package.objects.create(
            name     = "lodash",
            filePath = "../zipped_folders/lodash-master.zip"
        )
        package5 = Package.objects.create(
            name     = "nodist",
            filePath = "../zipped_folders/nodist-master.zip"
        )

        response1 = self.client.get(reverse("packages"))
        content1  = json.loads(response1.content.decode("utf8"))

        response2 = self.client.get(reverse("packages"), {"offset": content1["nextOffset"]})
        content2  = json.loads(response2.content.decode("utf8"))

        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)

        self.assertEqual(len(content1), 2)
        self.assertEqual(content1["packages"][0]["Name"], package1.name)
        self.assertEqual(content1["packages"][1]["Name"], package2.name)

        self.assertEqual(len(content2), 2)
        self.assertEqual(content2["packages"][0]["Name"], package3.name)
        self.assertEqual(content2["packages"][1]["Name"], package4.name)

    # Tests the rating endpoint. When a "GET" request is made, the total score and individual
    # sub scores should be returned. Each of these scores should be a float value between 0 
    # and 1, and there should be 5 sub scores. 
    def test_rating_endpoint(self):
        package = Package.objects.create(
            name      = "browserify",
            filePath  = "../zipped_folders/browserify-master.zip",
            githubUrl = "https://github.com/browserify/browserify"
        )

        response = self.client.get(
            reverse("rating", kwargs={"name": package.name}), 
        )

        responseBody = json.loads(response.content.decode("utf-8"))

        self.assertEqual(response.status_code, 200)

        for score in list(responseBody.values()):
            subScore = float(score)
            self.assertGreaterEqual(subScore, 0)
            self.assertLessEqual(subScore, 1)

class FunctionsTest(TestCase):
    def test_get_github_url_from_zipped_package(self):
        packageDirectory = '../zipped_folders/'
        
        cloudinaryUrl = get_github_url_from_zipped_package(packageDirectory + "cloudinary_npm-master.zip")
        browserifyUrl = get_github_url_from_zipped_package(packageDirectory + "browserify-master.zip")
        expressUrl    = get_github_url_from_zipped_package(packageDirectory + "express-master.zip")
        lodashUrl     = get_github_url_from_zipped_package(packageDirectory + "lodash-master.zip")
        nodistUrl     = get_github_url_from_zipped_package(packageDirectory + "nodist-master.zip")

        self.assertEqual(cloudinaryUrl, "https://github.com/cloudinary/cloudinary_npm")
        self.assertEqual(browserifyUrl, "http://github.com/browserify/browserify")
        self.assertEqual(expressUrl,    "https://github.com/expressjs/express")
        self.assertEqual(lodashUrl,     "")
        self.assertEqual(nodistUrl,     "https://github.com/marcelklehr/nodist")