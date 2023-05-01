from django.db import models
from django_extensions.db.models import (
    TimeStampedModel,
    ActivatorModel,
    TitleDescriptionModel)

from utils.model_abstracts import Model

# Create your models here.

class Contact(
    TimeStampedModel,
    ActivatorModel,
    TitleDescriptionModel,
    Model):
    '''contact model for the contact details of 
        user and message sent via the api'''
    email = models.EmailField(verbose_name='Email')

    def __str__(self) -> str:
        return f'{self.title}'

    class Meta:
        verbose_name_plural = 'Contacts'
    
