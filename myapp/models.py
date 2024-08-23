from django.db import models

class UserProfile(models.Model):
    username = models.CharField(max_length=100)
    email = models.EmailField()
    date_of_birth = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.username