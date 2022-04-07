from django.db import models


class Resume(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    fullname = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    job_title = models.CharField(max_length=100)
    pdf = models.FileField(upload_to='pdf/')

    def __str__(self):
        return self.fullname
