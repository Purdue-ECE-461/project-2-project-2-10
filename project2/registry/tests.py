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
        packageName = "UNIT_TEST"
        packagePath = "../zipped_folders/cloudinary_npm-master.zip"
        file        = open(packagePath, "rb")

        response = self.client.post(
            reverse('packages'), 
            data = {
                'name': packageName,
                'zipped_package': file
            }
        )

        package = Package.objects.all()[0]
        with open(package.filePath, "rb") as file:
            fileContent = file.readlines()[0]

            self.assertEqual(response.status_code, 201)
            self.assertEqual(fileContent, fileContent)
            self.assertEqual(package.name, packageName)
            self.assertEqual(package.githubUrl, "https://github.com/cloudinary/cloudinary_npm")
        
    # Test to see if a package is able to be downloaded from the server. 
    def test_get_package(self):
        packageName = "NAME"
        packagePath = "../project2/temp_files/cloudinary_npm-master.zip"
        Package.objects.create(
            name     = packageName,
            filePath = packagePath
        )

        response = self.client.get(
            reverse('package', kwargs={'name': packageName})
        )
        with open(packagePath, "rb") as file:
            self.assertEqual(file.read(), response.content)

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

        response2 = self.client.get(reverse("packages"), {"index": content1["nextIndex"]})
        content2  = json.loads(response2.content.decode("utf8"))

        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)

        self.assertEqual(len(content1), 2)
        self.assertEqual(content1["packages"][0]["name"], package1.name)
        self.assertEqual(content1["packages"][1]["name"], package2.name)

        self.assertEqual(len(content2), 2)
        self.assertEqual(content2["packages"][0]["name"], package3.name)
        self.assertEqual(content2["packages"][1]["name"], package4.name)

    # Tests to see if a package is only saved if it has high enough subscores. The Express 
    # package should have high enough sub scores, so it should be saved. Nodist should not
    # have high enough sub scores, so it should not be saved. 
    def test_ingestion(self):
        url = reverse("ingestion")

        goodFile = open("../zipped_folders/express-master.zip", "rb")
        badFile  = open("../zipped_folders/nodist-master.zip", "rb")
        
        responseGood = self.client.post(
            url, 
            data = {
                'name': "express",
                'zipped_package': goodFile
            }
        )
        responseBad = self.client.post(
            url, 
            data = {
                'name': "nodist",
                'zipped_package': badFile,
            }
        )

        responseBodyGood = json.loads(responseGood.content.decode("utf-8"))
        responseBodyBad  = json.loads(responseBad.content.decode("utf-8"))

        self.assertEqual(responseBodyGood["isFileSaved"], True)
        self.assertEqual(responseBodyBad["isFileSaved"], False)

        self.assertEqual(Package.objects.filter(name="express").count(), 1)
        self.assertEqual(Package.objects.filter(name="nodist").count(), 0)

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
        self.assertGreaterEqual(float(responseBody["score"]), 0)
        self.assertLessEqual(float(responseBody["score"]), 1)

        self.assertEqual(len(responseBody["subscores"]), 5)

        for score in responseBody["subscores"]:
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