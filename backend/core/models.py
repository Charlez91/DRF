from django.contrib.auth.models import User, AbstractUser
from django.db import models
from django_extensions.db.models import (
    TimeStampedModel,
    ActivatorModel,
    TitleDescriptionModel)
from PIL import Image

from utils.model_abstracts import Model

# Create your models here.

class Contact(
    TimeStampedModel,
    ActivatorModel,
    TitleDescriptionModel,
    Model):
    '''
    Contact model for the contact details of 
    user and message sent via the api
    '''
    email = models.EmailField(verbose_name='Email')

    def __str__(self) -> str:
        return f'{self.title}'

    class Meta:
        verbose_name_plural = 'Contacts'


class CustomUser(AbstractUser):
    gender_choices = (("M", "Male"),
                      ("F", "Female"))
    user_choices = (("vendor", "VENDOR"),
                      ("customer", "Customer"))
    gender = models.CharField(choices=gender_choices,max_length=20, null=True, blank=True)
    bio = models.TextField()
    date_of_birth = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null= True)
    country = models.CharField(max_length=100, null=True, blank=True)
    image = models.ImageField(default="default.jpg", upload_to="profile_pics")
    email_verified = models.BooleanField(default=False)



    def __str__(self) -> str:
            return f"{self.username}"

    def save(self) -> None:
        super().save()

        img = Image.open(self.image.path)

        if img.height > 150 or img.width > 150:
            output_size = (150, 150)  # 125,125 was used in flask example though
            img.thumbnail(output_size)
            img.save(self.image.path)


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

    def save(self) -> None:
        super().save()


class CustomerProfile(models.Model):
    """
    Customer model for external users
    """
    user_choices = (("vendor", "VENDOR"),
                      ("customer", "Customer"))
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    user_type = models.CharField(choices=user_choices,max_length=20, default="customer")
    store_address = models.TextField(null=True, blank=True)
    store_url = models.URLField(max_length=255, null=True, blank=True)
    avg_rating = models.DecimalField(decimal_places=2, max_digits=4, blank= True, null=True)

    def __str__(self) -> str:
            return f"{self.user.username} Customer Profile"

    def save(self) -> None:
        super().save()
