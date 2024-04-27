import os
from random import randint

from django.core.validators import MinValueValidator
from django.contrib.auth.models import AbstractUser
from django.db.models.query import QuerySet
from django.utils import timezone
from django.db import models
from django_extensions.db.models import (
    TimeStampedModel,
    ActivatorModel,
    TitleDescriptionModel)

from .tasks import process_user_image
from utils.model_abstracts import Model
from ecommerce.models import Item



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


def get_filename_ext(filepath):
    base_name = os.path.basename(filepath)
    name, ext = os.path.splitext(base_name)
    return name, ext

def upload_image_path(instance, filename)->str:
    new_filename = randint(1,3910209312)
    _, ext = get_filename_ext(filename)
    final_filename = f'{new_filename}{ext}'
    return "profile_pics/{final_filename}".format(final_filename=final_filename)


class CustomUser(AbstractUser):
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


class CommentManager(models.Manager):
    """
    Models Manager for Comments Model
    """
    def get_queryset(self) -> QuerySet:
        '''
        Return when called approved set to true
        and deleted false. to keep track of all comments
        '''
        return super().get_queryset().filter(approved=True).filter(deleted=False)


class Comment(models.Model):
    """
    Comment/Rating Model for comments/ratings of various vendors
    """

    name = models.CharField(max_length=250, null=False, blank=False)#commenters name
    email = models.EmailField()#commenters email
    comment = models.TextField(null=True, blank=True)
    vendor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='comments')#vendor receiving rating
    #might add item foreign key relation field. to enable item rating
    item = models.ForeignKey(Item, on_delete=models.SET_NULL, blank=True, null=True)
    date_created = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(auto_now=True)
    approved = models.BooleanField(default=True)
    deleted = models.BooleanField(default=False)
    rating = models.DecimalField(decimal_places=2, max_digits=4, validators=[MinValueValidator(1, message="Rating must not be less than 1")])

    objects = CommentManager()


    def save_user_avg_rating(self):
        total = int(Comment.objects.filter(vendor=self.vendor).count())
        old_avg_rating = self.vendor.avg_rating
        current_rating = self.rating
        new_sum = float(old_avg_rating * (total-1)) + float(current_rating)
        #implement validations against lte zero values for current_rating and gt 2dp in serializers or here
        new_avg_rating = new_sum/total
        self.vendor.avg_rating = round(new_avg_rating, 2)#implement algorithm to make it rounded off to 2dp
        self.vendor.save()

    def del_user_avg_rating(self):
        old_avg_rating = self.vendor.avg_rating
        current_rating = self.rating
        total = int(Comment.objects.filter(vendor=self.vendor).count()+1)
        new_sum = float((total * old_avg_rating) - current_rating)
        new_avg_ratings = new_sum/(total-1)
        self.vendor.avg_rating = round(new_avg_ratings, 2)
        self.vendor.save()

    def save(self, *args, op=None,**kwargs) -> None:
        print("saving")
        super().save(*args, **kwargs)
        self.save_user_avg_rating()#updates average rating

    def delete(self, *args, **kwargs) -> None:
        print("deleting")
        self.deleted = True
        #self.save(op="Delete")#no need for this again
        super().save(*args, **kwargs)#we can call save method of the parent class directly
        #REMEMBER to update algorithm incase of delete of comment/rating
        self.del_user_avg_rating()
        #return super().delete(*args, **kwargs)#no need for this since we implementing soft delete

    def __str__(self):
        return f"{self.email} Comment"

    class Meta:
        verbose_name = "Comment"
        verbose_name_plural = "Comments"
        ordering = ('-date_created',)


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

