from django.db import models

class Package(models.Model):
    name     = models.TextField()
    filePath = models.TextField()
    isSecret = models.BooleanField(default=False)