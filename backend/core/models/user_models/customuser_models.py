import os
from random import randint

from django.db import models
from django.contrib.auth.models import AbstractUser

from core.tasks import process_user_image

#helper functions
def get_filename_ext(filepath):
    base_name = os.path.basename(filepath)
    name, ext = os.path.splitext(base_name)
    return name, ext

def upload_image_path(instance, filename)->str:
    new_filename = randint(1,3910209312)
    _, ext = get_filename_ext(filename)
    final_filename = f'{new_filename}{ext}'
    return "profile_pics/{final_filename}".format(final_filename=final_filename)

#model classes
class CustomUser(AbstractUser):
    """
    Base User Class
    """
    gender_choices = (("M", "Male"),
                      ("F", "Female"))
    email = models.EmailField(unique=True, 
                error_messages={"unique": "A user with that email already exists.",},)
    gender = models.CharField(choices=gender_choices,max_length=20, null=True, blank=True)
    bio = models.TextField()
    date_of_birth = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null= True)
    country = models.CharField(max_length=100, null=True, blank=True)
    image = models.ImageField(default="default.jpg", upload_to=upload_image_path)#profile
    email_verified = models.BooleanField(default=False)
    avg_rating = models.DecimalField(decimal_places=2, max_digits=4, default=0)
    #amount earned, amount paid out

    def __str__(self) -> str:
            return f"{self.username}"
    
    def process_image(self)->str:
        process_user_image.delay(self.image.path)
        return "done"
    
    def get_comments(self):
        '''
        Gets all comment/ratings on user
        '''
        return self.comments.filter(approved=True).filter(deleted=False)

    def save(self, *args, **kwargs) -> None:
        print("saving")
        super().save(*args, **kwargs)
        #process_user_image(self)#to reduce overhead on saving saving opeations

    class Meta:
        verbose_name = "CustomUser"
        verbose_name_plural = "CustomUsers"
        ordering = ["id"]
