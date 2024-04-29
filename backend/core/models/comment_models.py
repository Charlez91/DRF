from django.db import models
from django.db.models.query import QuerySet
from django.core.validators import MinValueValidator
from django.utils import timezone

from .user_models import CustomUser
from ecommerce.models import Item

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
