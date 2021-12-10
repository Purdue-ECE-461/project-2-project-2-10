from django.db import models

class Package(models.Model):
    name       = models.TextField()
    package_id = models.TextField(unique=True)
    version    = models.TextField()

    file_path  = models.TextField()
    is_secret  = models.BooleanField(default=False)
    github_url = models.TextField(default="")
    js_program = models.TextField(default="")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["name", "version"], name="uniquePackage")
        ]

    def to_dict(self):
        return {
            "Name":    self.name,
            "Version": self.version,
            "ID":      self.package_id
        }
