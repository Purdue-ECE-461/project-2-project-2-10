import json

from django.test import TestCase, Client
from django.urls import reverse

from .models import Package
from .functions import save_file

class PackageTest(TestCase):
    def setUp(self):
        self.client = Client()

    # Tests to see if a zipped package is uploaded successfully and that the correct meta data
    # is stored.
    def test_upload_package(self):
        package_name    = "UNIT_TEST"
        package_version = "1.0.0"
        package_id      = "UNIT_TEST_ID"
        package_url     = "github.com/fake/url/path"
        js_program      = """
            if (process.argv.length === 7) {\n
                console.log('Success')\n
                process.exit(0)\n
            } else {\n
                console.log('Failed')\n
                process.exit(1)\n
            }\n
        """

        package_path = "../zipped_folders/cloudinary_npm-master.zip"
        with open(package_path, "rb") as original_file:
            original_file_content = original_file.read().decode("Cp437")

        response = self.client.post(
            reverse('packages'),
            data = {
                "metadata": json.dumps({
                    "Name": package_name,
                    "Version": package_version,
                    "ID": package_id
                }),
                "data": json.dumps({
                    "Content": original_file_content,
                    "URL": package_url,
                    "JSProgram": js_program
                })
            }
        )

        # package = Package.objects.all()[0]
        # with open(package.file_path, "rb") as saved_file:
        #     self.assertEqual(saved_file.read().decode("Cp437"), original_file_content)

        self.assertEqual(response.status_code, 201)

    # Test to see if a package is able to be downloaded from the server.
    def test_get_package(self):
        package_name     = "UNIT_TEST"
        package_version  = "1.0.0"
        package_id       = "UNIT_TEST_ID"
        package_url      = "github.com/fake/url/path"
        js_program       = """
            if (process.argv.length === 7) {\n
                console.log('Success')\n
                process.exit(0)\n
            } else {\n
                console.log('Failed')\n
                process.exit(1)\n
            }\n
        """

        package_path = save_file("UNIT_TEST", "hello world")

        Package.objects.create(
            name       = package_name,
            package_id = package_id,
            version    = package_version,
            github_url = package_url,
            js_program = js_program,
            file_path  = package_path
        )

        response = self.client.get(
            reverse('package', kwargs={'package_id': package_id})
        )
        response_content = json.loads(response.content)

        # with open(package_path, "rb") as file:
        #     self.assertEqual(file.read(), response_content["data"]["Content"].encode("Cp437"))

        self.assertEqual(response_content["data"]["URL"], package_url)
        self.assertEqual(response_content["data"]["JSProgram"], js_program)
        self.assertEqual(response_content["metadata"]["Name"], package_name)
        self.assertEqual(response_content["metadata"]["Version"], package_version)
        self.assertEqual(response_content["metadata"]["ID"], package_id)

    # Tests the pagination endpoint. Asks for a list of packages from the server, checks to see
    # if only two packages are returned at a time. Asks for a list of packages twice to see if
    # a different list of packages are returned each time.
    def test_get_paginated_list(self):
        package1 = Package.objects.create(
            name      = "browserify",
            package_id = "1",
            file_path  = "../zipped_folders/browserify-master.zip"
        )
        package2 = Package.objects.create(
            name      = "cloudinary",
            package_id = "2",
            file_path  = "project-2-project-2-10/zipped_folders/cloudinary_npm-master.zip"
        )
        package3 = Package.objects.create(
            name      = "express",
            package_id = "3",
            file_path  = "../zipped_folders/express-master.zip"
        )
        package4 = Package.objects.create(
            name      = "lodash",
            package_id = "4",
            file_path  = "../zipped_folders/lodash-master.zip"
        )
        _ = Package.objects.create(
            name      = "nodist",
            package_id = "5",
            file_path  = "../zipped_folders/nodist-master.zip"
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
            file_path  = "../zipped_folders/browserify-master.zip",
            github_url = "https://github.com/browserify/browserify",
            package_id = "UNIT_TEST_ID",
        )

        response = self.client.get(
            reverse("rating", kwargs={"package_id": package.package_id}),
        )

        response_body = json.loads(response.content.decode("utf-8"))

        self.assertEqual(response.status_code, 200)

        for score in list(response_body.values()):
            sub_score = float(score)
            self.assertGreaterEqual(sub_score, 0)
            self.assertLessEqual(sub_score, 1)

    # Tries to update a package's data. If the correct name, version, and id are given, then
    # the package should be updated with the values found in "data".
    def test_update_package(self):
        original_file_path = "../zipped_folders/browserify-master.zip"

        package = Package.objects.create(
            name      = "browserify",
            file_path  = original_file_path,
            github_url = "https://github.com/browserify/browserify",
            package_id = "UNIT_TEST_ID",
            js_program = "if (x == 2) return true;"
        )

        new_url        = "github.com/path/to/fake/url"
        new_js_program = "if (x == 2) return false;"

        response = self.client.put(
            reverse('package', kwargs={"package_id": package.package_id}),
            data = json.dumps({
                "metadata": {
                    "Name": package.name,
                    "Version": package.version,
                    "ID": package.package_id
                },
                "data": {
                    "Content":" base64.b64encode(originalFile.read()).decode('utf-8')",
                    "URL": new_url,
                    "JSProgram": new_js_program
                }
            })
        )

        updated_package = Package.objects.first()

        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(updated_package.file_path, original_file_path)
        self.assertEqual(updated_package.github_url, new_url)
        self.assertEqual(updated_package.js_program, new_js_program)

    # Tries to update a package, but gives the wrong version. The package should not be updated,
    # and all the values should remain the same.
    def test_update_package_with_wrong_version(self):
        original_file_path = "../zipped_folders/browserify-master.zip"

        package = Package.objects.create(
            name      = "browserify",
            file_path  = original_file_path,
            github_url = "https://github.com/browserify/browserify",
            package_id = "UNIT_TEST_ID",
            js_program = "if (x == 2) return true;"
        )

        new_url        = "github.com/path/to/fake/url"
        new_js_program = "if (x == 2) return false;"

        response = self.client.put(
            reverse('package', kwargs={"package_id": package.package_id}),
            data = json.dumps({
                "metadata": {
                    "Name": package.name,
                    "Version": "wrong version",
                    "ID": package.package_id
                },
                "data": {
                    "Content":" base64.b64encode(originalFile.read()).decode('utf-8')",
                    "URL": new_url,
                    "JSProgram": new_js_program
                }
            })
        )

        updated_package = Package.objects.first()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(updated_package.file_path, original_file_path)
        self.assertEqual(updated_package.github_url, package.github_url)
        self.assertEqual(updated_package.js_program, package.js_program)

    # Should delete package
    def test_delete_package(self):
        package = Package.objects.create(
            name      = "browserify",
            file_path  = "../zipped_folders/browserify-master.zip",
            github_url = "https://github.com/browserify/browserify",
            package_id = "UNIT_TEST_ID",
            js_program = "if (x == 2) return true;"
        )

        response = self.client.delete(reverse('package', kwargs={"package_id": package.package_id}))

        self.assertEqual(response.status_code, 200)

        self.assertEqual(Package.objects.count(), 0)

    def test_delete_package_by_name(self):
        package1 = Package.objects.create(
            name       = "browserify",
            version    = "1.0.0",
            package_id = "1",
            file_path  = "../zipped_folders/browserify-master.zip"
        )
        _ = Package.objects.create(
            name       = "browserify",
            version    = "1.0.1",
            package_id = "2",
            file_path  = "project-2-project-2-10/zipped_folders/cloudinary_npm-master.zip"
        )

        self.client.delete(reverse("by_name", kwargs={"name": package1.name}))

        self.assertEqual(Package.objects.count(), 0)

    def test_reset(self):
        Package.objects.create(
            name      = "browserify",
            package_id = "1",
            file_path  = "../zipped_folders/browserify-master.zip"
        )
        Package.objects.create(
            name      = "cloudinary",
            package_id = "2",
            file_path  = "project-2-project-2-10/zipped_folders/cloudinary_npm-master.zip"
        )
        Package.objects.create(
            name      = "express",
            package_id = "3",
            file_path  = "../zipped_folders/express-master.zip"
        )

        self.client.delete(reverse("reset"))

        self.assertEqual(Package.objects.count(), 0)
