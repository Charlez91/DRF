import uuid

from django.db import models

class Model(models.Model):
    '''
    Instead of using the normal id field we 
    using uuid4 to generate random unique id
    '''
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    
    class Meta:
        abstract = True