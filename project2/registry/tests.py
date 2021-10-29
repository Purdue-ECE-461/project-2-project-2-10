import json

from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from .models import *

class PackageTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_upload_package(self):
        packageName = "UNIT_TEST"
        packagePath = "/Users/johnbensen/Documents/ECE/ECE461/PROJECT_2/project-2-project-2-10/zipped_folders/cloudinary_npm-master.zip"
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
        
    def test_get_package(self):
        packageName = "NAME"
        packagePath = "/Users/johnbensen/Documents/ECE/ECE461/PROJECT_2/project-2-project-2-10/project2/temp_files/cloudinary_npm-master.zip"
        Package.objects.create(
            name     = packageName,
            filePath = packagePath
        )

        response = self.client.get(
            reverse('package', kwargs={'name': packageName})
        )
        with open(packagePath, "rb") as file:
            self.assertEqual(file.read(), response.content)

    def test_get_paginated_list(self):
        package1 = Package.objects.create(
            name     = "browserify",
            filePath = "/Users/johnbensen/Documents/ECE/ECE461/PROJECT_2/project-2-project-2-10/zipped_folders/browserify-master.zip"
        )
        package2 = Package.objects.create(
            name     = "cloudinary",
            filePath = "project-2-project-2-10/zipped_folders/cloudinary_npm-master.zip"
        )
        package3 = Package.objects.create(
            name     = "express",
            filePath = "/Users/johnbensen/Documents/ECE/ECE461/PROJECT_2/project-2-project-2-10/zipped_folders/express-master.zip"
        )
        package4 = Package.objects.create(
            name     = "lodash",
            filePath = "/Users/johnbensen/Documents/ECE/ECE461/PROJECT_2/project-2-project-2-10/zipped_folders/lodash-master.zip"
        )
        package5 = Package.objects.create(
            name     = "nodist",
            filePath = "/Users/johnbensen/Documents/ECE/ECE461/PROJECT_2/project-2-project-2-10/zipped_folders/nodist-master.zip"
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