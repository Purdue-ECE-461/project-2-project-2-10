import json
import base64

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

        packagePath         = "../zipped_folders/cloudinary_npm-master.zip"
        originalFile        = open(packagePath, "rb")
        originalFileContent = originalFile.read().decode("Cp437")

        response = self.client.post(
            reverse('packages'), 
            data = {
                "metadata": json.dumps({
                    "Name": packageName,
                    "Version": packageVersion,
                    "ID": packageID
                }),
                "data": json.dumps({
                    "Content": originalFileContent,
                    "URL": packageURL,
                    "JSProgram": jsProgram
                })
            }
        )

        package = Package.objects.all()[0]
        with open(package.filePath, "rb") as savedFile:
            self.assertEqual(savedFile.read().decode("Cp437"), originalFileContent)

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
            reverse('package', kwargs={'id': packageID})
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
            name      = "browserify",
            packageId = "1",
            filePath  = "../zipped_folders/browserify-master.zip"
        )
        package2 = Package.objects.create(
            name      = "cloudinary",
            packageId = "2",
            filePath  = "project-2-project-2-10/zipped_folders/cloudinary_npm-master.zip"
        )
        package3 = Package.objects.create(
            name      = "express",
            packageId = "3",
            filePath  = "../zipped_folders/express-master.zip"
        )
        package4 = Package.objects.create(
            name      = "lodash",
            packageId = "4",
            filePath  = "../zipped_folders/lodash-master.zip"
        )
        package5 = Package.objects.create(
            name      = "nodist",
            packageId = "5",
            filePath  = "../zipped_folders/nodist-master.zip"
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
            githubUrl = "https://github.com/browserify/browserify",
            packageId = "UNIT_TEST_ID",
        )

        response = self.client.get(
            reverse("rating", kwargs={"id": package.packageId}), 
        )

        responseBody = json.loads(response.content.decode("utf-8"))

        self.assertEqual(response.status_code, 200)

        for score in list(responseBody.values()):
            subScore = float(score)
            self.assertGreaterEqual(subScore, 0)
            self.assertLessEqual(subScore, 1)

    # Tries to update a package's data. If the correct name, version, and id are given, then the package
    # should be updated with the values found in "data".
    def test_update_package(self):
        originalFilePath = "../zipped_folders/browserify-master.zip"

        package = Package.objects.create(
            name      = "browserify",
            filePath  = originalFilePath,
            githubUrl = "https://github.com/browserify/browserify",
            packageId = "UNIT_TEST_ID",
            jsProgram = "if (x == 2) return true;"
        )

        newUrl       = "github.com/path/to/fake/url"
        newJsProgram = "if (x == 2) return false;"

        response = self.client.put(
            reverse('package', kwargs={"id": package.packageId}), 
            data = json.dumps({
                "metadata": {
                    "Name": package.name,
                    "Version": package.version,
                    "ID": package.packageId
                },
                "data": {
                    "Content":" base64.b64encode(originalFile.read()).decode('utf-8')",
                    "URL": newUrl,
                    "JSProgram": newJsProgram
                }
            })  
        )

        updatedPackage = Package.objects.first()

        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(updatedPackage.filePath, originalFilePath)
        self.assertEqual(updatedPackage.githubUrl, newUrl)
        self.assertEqual(updatedPackage.jsProgram, newJsProgram)

    # Tries to update a package, but gives the wrong version. The package should not be updated,
    # and all the values should remain the same. 
    def test_update_package_with_wrong_version(self):
        originalFilePath = "../zipped_folders/browserify-master.zip"

        package = Package.objects.create(
            name      = "browserify",
            filePath  = originalFilePath,
            githubUrl = "https://github.com/browserify/browserify",
            packageId = "UNIT_TEST_ID",
            jsProgram = "if (x == 2) return true;"
        )

        newUrl       = "github.com/path/to/fake/url"
        newJsProgram = "if (x == 2) return false;"

        response = self.client.put(
            reverse('package', kwargs={"id": package.packageId}), 
            data = json.dumps({
                "metadata": {
                    "Name": package.name,
                    "Version": "wrong version",
                    "ID": package.packageId
                },
                "data": {
                    "Content":" base64.b64encode(originalFile.read()).decode('utf-8')",
                    "URL": newUrl,
                    "JSProgram": newJsProgram
                }
            })  
        )

        updatedPackage = Package.objects.first()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(updatedPackage.filePath, originalFilePath)
        self.assertEqual(updatedPackage.githubUrl, package.githubUrl)
        self.assertEqual(updatedPackage.jsProgram, package.jsProgram)

    # Should delete package
    def test_delete_package(self):
        package = Package.objects.create(
            name      = "browserify",
            filePath  = "../zipped_folders/browserify-master.zip",
            githubUrl = "https://github.com/browserify/browserify",
            packageId = "UNIT_TEST_ID",
            jsProgram = "if (x == 2) return true;"
        )

        response = self.client.delete(reverse('package', kwargs={"id": package.packageId}))

        self.assertEqual(response.status_code, 200)

        self.assertEqual(Package.objects.count(), 0)

    def test_delete_package_by_name(self):
        package1 = Package.objects.create(
            name      = "browserify",
            version   = "1.0.0",
            packageId = "1", 
            filePath  = "../zipped_folders/browserify-master.zip"
        )
        package2 = Package.objects.create(
            name      = "browserify",
            version   = "1.0.1",
            packageId = "2",
            filePath  = "project-2-project-2-10/zipped_folders/cloudinary_npm-master.zip"
        )

        self.client.delete(reverse("byName", kwargs={"name": package1.name}))

        self.assertEqual(Package.objects.count(), 0)
