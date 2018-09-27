from django.db import models
 
 #WARNING: NOT USED AS OF NOW
class UploadFile(models.Model):
    file = models.FileField(upload_to='files/%Y/%m/%d')