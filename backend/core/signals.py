from django.dispatch import receiver
from django.db.models.signals import post_save
from rest_framework.authtoken.models import Token

from core.models import CustomUser, CustomerProfile, EmployeeProfile

@receiver(post_save, sender = CustomUser, weak = False)
def report_uploaded(sender, instance, created, **kwargs):
    if created:
        Token.objects.create(user = instance)


#still considering using signals for profile creation and update
#@receiver(post_save, sender=CustomUser)
def create_profile(sender, instance, created, **kwargs):
    if created:
        if instance.is_staff:
            EmployeeProfile.objects.create(user=instance)
        else:
            CustomerProfile.objects.create(user=instance)

#@receiver(post_save, sender=CustomUser)
def save_profile(sender, instance, created, **kwargs):
    if created is False:
        if instance.is_staff:
            instance.employeeprofile.save()
        else:
            instance.customerprofile.save()
