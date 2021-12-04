import json

from django.test import TestCase, Client
from django.urls import reverse

from .models import Package
from .functions import *

class PackageTest(TestCase):
    def setUp(self):
        self.client     = Client()
        self.package_id = 0
        self.file_path  = "../zipped_folders/temp.txt"
        self.content    = "hello world"

    @classmethod
    def tearDownClass(cls):
        super(PackageTest, cls).tearDownClass()

    def create_package(self, name, github_url="github.com/fake/repo", version="1.0.0"):
        package = Package.objects.create(
            name       = name,
            package_id = str(self.package_id),
            version    = version,
            file_path  = name,
            github_url = github_url
        )

        self.package_id += 1

        return package

    def test_post_package(self):
        package_name    = "name"
        package_version = "1.0.1"
        package_id      = "1"
        package_js      = "js"
        with open("../zipped_folders/browserify-master.zip", "rb") as file:
            package_content = file.read().decode("Cp437")

        response = self.client.post(
            reverse('packages'),
            data = {
                "metadata": json.dumps({
                    "Name": package_name,
                    "Version": package_version,
                    "ID": package_id
                }),
                "data": json.dumps({
                    "Content": package_content,
                    "JSProgram": package_js
                })
            }
        )

        created_package         = Package.objects.first()
        created_package_content = get_file_content(created_package.file_path)
        created_package_url     = created_package.github_url

        self.assertEqual(response.status_code, 201)
        self.assertEqual(created_package_content, package_content)
        self.assertEqual(created_package_url, "http://github.com/browserify/browserify")

    def test_get_packages(self):
        package1 = self.create_package("name1")
        package2 = self.create_package("name2")
        package3 = self.create_package("name3")
        package4 = self.create_package("name4")

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

    def test_get_package(self):
        zipped_file = "../zipped_folders/browserify-master.zip"
        name        = "browserify-master"
        with open(zipped_file, "rb") as file:
            save_file(name, file.read())
        package = self.create_package(name)

        response = self.client.get(
            reverse("package", kwargs={'package_id': package.package_id}))
        response_content = json.loads(response.content)

        self.assertEqual(response_content["data"]["URL"],         package.github_url)
        self.assertEqual(response_content["data"]["JSProgram"],   package.js_program)
        self.assertEqual(response_content["metadata"]["Name"],    package.name)
        self.assertEqual(response_content["metadata"]["Version"], package.version)
        self.assertEqual(response_content["metadata"]["ID"],      package.package_id)

        with open(zipped_file, "rb") as file:
            self.assertEqual(response_content["data"]["Content"], file.read().decode("CP437"))

    def test_delete_package(self):
        package = self.create_package("name")

        self.client.delete(reverse("package", kwargs={'package_id': package.package_id}))

        self.assertEqual(Package.objects.count(), 0)

    def test_get_rating(self):
        package = self.create_package("name")
        response = self.client.get(
            reverse("rating", kwargs={"package_id": package.package_id}),
        )

        response_body = json.loads(response.content.decode("utf-8"))

        self.assertEqual(response.status_code, 200)

        for score in list(response_body.values()):
            sub_score = float(score)
            self.assertGreaterEqual(sub_score, 0)
            self.assertLessEqual(sub_score, 1)

    def test_reset(self):
        self.create_package("name1")
        self.create_package("name2")
        self.create_package("name3")

        self.client.delete(reverse("reset"))

        self.assertEqual(Package.objects.count(), 0)

    def test_ingestion(self):
        package_name    = "name"
        package_version = "1.0.1"
        package_id      = "1"
        package_url     = "https://github.com/expressjs/express"
        package_js      = "js"

        response = self.client.post(
            reverse('packages'),
            data = {
                "metadata": json.dumps({
                    "Name": package_name,
                    "Version": package_version,
                    "ID": package_id
                }),
                "data": json.dumps({
                    "URL": package_url,
                    "JSProgram": package_js
                })
            }
        )

        self.assertEqual(response.status_code, 201)

        ingested_package      = Package.objects.first()
        ingested_file_content = get_file_content(ingested_package.file_path)
        with open("../zipped_folders/express-master.zip", "rb") as file:
            self.assertEqual(ingested_file_content, file.read().decode("Cp437"))

    def test_failed_ingestion(self):
        package_name    = "name"
        package_version = "1.0.1"
        package_id      = "1"
        package_url     = "https://github.com/nullivex/nodist"
        package_js      = "js"

        response = self.client.post(
            reverse('packages'),
            data = {
                "metadata": json.dumps({
                    "Name": package_name,
                    "Version": package_version,
                    "ID": package_id
                }),
                "data": json.dumps({
                    "URL": package_url,
                    "JSProgram": package_js
                })
            }
        )

        self.assertEqual(response.status_code, 400)

    def test_get_package_scores(self):
        pass
        # browserify_scores = get_github_scores("https://github.com/browserify/browserify")
        # cloudinary_scores = get_github_scores("https://github.com/cloudinary/cloudinary_npm")
        # express_scores    = get_github_scores("https://github.com/expressjs/express")
        # nodist_scores     = get_github_scores("https://github.com/nullivex/nodist")
        # lodash_scores     = get_github_scores("https://github.com/lodash/lodash")

        # print(browserify_scores.keys())

        # print("browserify: ", browserify_scores.values())
        # print("cloudinary: ", cloudinary_scores.values())
        # print("express:    ", express_scores.values())
        # print("nodist:     ", nodist_scores.values())
        # print("lodash:     ", lodash_scores.values())
