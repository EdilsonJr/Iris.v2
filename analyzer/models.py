from django.db import models


class Analyzer(models.Model):
    version = models.CharField(max_length=100, null=False)
    name = models.CharField(primary_key=True, max_length=100, null=False)

    model = models.BinaryField(max_length=None, null=True)
    word_vec = models.BinaryField(max_length=None, null=True)
    label_encoder = models.BinaryField(max_length=None, null=True)

    status = models.CharField(max_length=100, null=True)
    
    precision = models.FloatField(null=True)
    recall = models.FloatField(null=True)
    accuracy = models.FloatField(null=True)

    class Meta:
        db_table = "analyzer"


class Data(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    key_word = models.CharField(max_length=100, null=True)
    file = models.BinaryField(max_length=None, null=True)
    user_key = models.CharField(max_length=100, null=True)
    results = models.BinaryField(max_length=None, null=True)
    raw_results = models.BinaryField(max_length=None, null=True)
    zipped_results = models.BinaryField( max_length=None, null=True)


    class Meta:
        db_table = "data"
