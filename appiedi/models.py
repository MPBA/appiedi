from django.db import models

# Create your models here.
class TelecomDataset(models.Model):
    humidity = models.FloatField()
    pressure = models.FloatField()
    temperature = models.FloatField()
    co = models.FloatField()
    altitude = models.FloatField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    mtl_timestamp = models.DateTimeField()
    the_geom = models.TextField(blank=True) # This field type is a guess.
    accuracy = models.FloatField()
    provider = models.IntegerField()
    speed = models.FloatField()
    id = models.BigIntegerField(primary_key=True)
    class Meta:
        managed = False
        db_table = 'telecom_dataset'
