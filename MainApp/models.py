from django.db import models

# Create your models here.

class Data(models.Model):
    filename = models.CharField(max_length=50,blank=True,null=True)
    timeframe = models.IntegerField(blank=True,null=True)
    convertedfile_location = models.CharField(max_length=500,blank=True,null=True)

    def __str__(self):
        return f"{self.filename},{self.timeframe},{self.convertedfile_location}"
    