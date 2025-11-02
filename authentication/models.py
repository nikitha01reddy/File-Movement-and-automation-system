from django.db import models

class UserProfile(models.Model):
    userid = models.CharField(max_length=100,primary_key=True)
    name = models.CharField(max_length=50)
    password = models.CharField(max_length=128)  # Store hashed passwords
    department = models.CharField(max_length=100)
    school = models.CharField(max_length=50, blank=True, null=True) #optional
    section = models.CharField(max_length=50, blank=True, null=True) #optional
    cell = models.CharField(max_length=50, blank=True, null=True) #optional
    center = models.CharField(max_length=50, blank=True, null=True) #optional
    laboratory = models.CharField(max_length=50, blank=True, null=True) #optional
    club = models.CharField(max_length=50, blank=True, null=True) #option
    office = models.CharField(max_length=50, blank=True, null=True) #option

    def __str__(self):
        return self.name
