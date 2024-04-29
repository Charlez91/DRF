from django.db import models

from .customuser_models import CustomUser

class CustomerProfile(models.Model):
    """
    Customer model for external users
    """
    user_choices = (("vendor", "VENDOR"),
                      ("buyer", "BUYER"))
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    user_type = models.CharField(choices=user_choices,max_length=20, default="buyer")
    store_address = models.TextField(null=True, blank=True)
    store_url = models.URLField(max_length=255, null=True, blank=True)

    def __str__(self) -> str:
            return f"{self.user.username} Customer Profile"
    
    class Meta:
        verbose_name = "CustomerProfile"
        verbose_name_plural = "CustomerProfiles"
        ordering = ["id"]

