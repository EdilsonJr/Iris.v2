# Generated by Django 3.2.3 on 2021-10-17 15:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analyzer', '0002_auto_20211013_1915'),
    ]

    operations = [
        migrations.AddField(
            model_name='data',
            name='raw_results',
            field=models.BinaryField(null=True),
        ),
    ]