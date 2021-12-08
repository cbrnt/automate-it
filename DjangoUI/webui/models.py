from django.db import models


class Ui(models.Model):
    name = models.CharField(max_length=20)
    lastname = models.CharField(max_length=20)
    position = models.CharField(max_length=20)
    card = models.IntegerField()
    place = models.CharField(max_length=3)
    date = models.DateTimeField(auto_now_add=True, db_index=True)

# Create your models here.
