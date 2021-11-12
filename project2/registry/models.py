from django.db import models

class BaseModel():
    def to_dict(self):
        returnDict = {}

        for key in self.__dict__.keys():
            if key not in ['_state', 'id']:
                returnDict[key] = self.__dict__[key]

        return returnDict

class Package(models.Model, BaseModel):
    name      = models.TextField()
    packageId = models.TextField()
    version   = models.TextField()

    filePath  = models.TextField()
    isSecret  = models.BooleanField(default=False)
    githubUrl = models.TextField(default="")
    jsProgram = models.TextField(default="")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["name", "packageId", "version"], name="uniquePackage")
        ]

    def to_dict(self):
        return {
            "Name":    self.name,
            "Version": self.version,
            "ID":      self.packageId
        }


