# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AreaScoring(models.Model):
    id = models.AutoField(primary_key=True)
    step_id = models.IntegerField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = '"mart"."area_scoring"'
        unique_together = (('step_id', 'latitude', 'longitude'),)

class Crime(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.DateField(null=False)
    date_excitation = models.DateField()
    crime_title = models.CharField(null=False)
    crime_level = models.IntegerField()
    latitude = models.FloatField(null=False)
    longitude = models.FloatField(null=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = '"public"."crime"'
