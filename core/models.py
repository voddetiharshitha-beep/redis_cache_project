from django.db import models

# Create your models here.
from django.db import models


class VehicleType(models.Model):
    name = models.CharField(max_length=100)
    capacity = models.IntegerField()
    base_fare = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
class ApplicationConfig(models.Model):
     key = models.CharField(max_length=100, unique=True)
     value = models.CharField(max_length=255)

     def __str__(self):
        return self.key
    
class CancellationReason(models.Model):
    reason = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.reason