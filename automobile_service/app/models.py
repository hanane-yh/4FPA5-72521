from django.db import models


class Automobile(models.Model):
    manufacturer = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.manufacturer} {self.model}"


class Part(models.Model):
    automobile = models.ForeignKey(Automobile, related_name='parts', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} of {self.automobile}"


class PartFile(models.Model):
    part = models.ForeignKey(Part, related_name='files', on_delete=models.CASCADE)
    file = models.FileField(upload_to='part_files/')

    def __str__(self):
        return f"File for {self.part.name}"
