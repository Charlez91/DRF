from django.db import models

from .customuser_models import CustomUser

class EmployeeProfile(models.Model):
    """
    Employee model for inhouse users
    """
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    skills = models.JSONField(null=True, blank=True)
    department = models.CharField(max_length=255, blank=True, null=True)
    position = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self) -> str:
            return f"{self.user.username} Employee Profile"

