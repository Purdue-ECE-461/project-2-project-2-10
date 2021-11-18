import json

from django.test import TestCase, Client
from django.urls import reverse

from .models import Package
from .functions import get_file_content, save_file

class PackageTest(TestCase):
    def setUp(self):
        self.client     = Client()
        self.package_id = 0
        self.file_path  = "../zipped_folders/temp.txt"
        self.content    = "hello world"

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

    def test_post_packages(self):
        package_name    = "name"
        package_version = "1.0.1"
        package_id      = "1"
        package_content = self.content
        package_url     = "github"
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
                    "Content": package_content,
                    "URL": package_url,
                    "JSProgram": package_js
                })
            }
        )

        saved_package = Package.objects.first()
        saved_content = get_file_content(saved_package.file_path)

        self.assertEqual(response.status_code, 201)

        self.assertEqual(saved_package.name, package_name)
        self.assertEqual(saved_package.package_id, package_id)
        self.assertEqual(saved_content, package_content)

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
        package = self.create_package("name")
        save_file(package.name, self.content)

        response = self.client.get(
            reverse("package", kwargs={'package_id': package.package_id}))
        response_content = json.loads(response.content)

        self.assertEqual(response_content["data"]["URL"],         package.github_url)
        self.assertEqual(response_content["data"]["JSProgram"],   package.js_program)
        self.assertEqual(response_content["metadata"]["Name"],    package.name)
        self.assertEqual(response_content["metadata"]["Version"], package.version)
        self.assertEqual(response_content["metadata"]["ID"],      package.package_id)

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
