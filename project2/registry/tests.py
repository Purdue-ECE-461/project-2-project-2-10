from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from .models import *

class PackageTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_upload_package(self):
        fileContent = b"Hello Django"
        packageName = "UNIT_TEST"
        file        = SimpleUploadedFile("test_upload.txt", fileContent, content_type="txt")

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
        fileContent   = b"Testing get package"
        packageName   = "test_get"
        directoryPath = "/Users/johnbensen/Documents/ECE/ECE461/PROJECT_2/project-2-project-2-10/project2/temp_files/"
        filePath      = directoryPath + packageName + ".txt"
        with open(filePath, 'wb') as file:
            file.write(fileContent)

        Package.objects.create(
            name     = packageName,
            filePath = filePath
        )

        response = self.client.get(
            reverse('package', kwargs={'name': packageName})
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, fileContent)