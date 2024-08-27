from django.db import models

class UserProfile(models.Model):
    username = models.CharField(max_length=100)
    email = models.EmailField()
    date_of_birth = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.username
    
class User(models.Model):
    username = models.CharField(max_length=150, null=False, blank=False)
    

class Inquiry(models.Model):
    username = models.CharField(max_length=255)
    brand = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField()

    def __str__(self):
        return f"Inquiry from {self.username}"