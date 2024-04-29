from rest_framework.serializers import ModelSerializer  # CharField can be imported here too but not adviced
from rest_framework.fields import (
    CharField, EmailField,
    ) #CharField should be imported here(directly)

from core.models import Contact

class ContactSerializer(ModelSerializer):
    '''
    Serializer class for contact view
    '''
    name = CharField(source='title', required=True)
    message = CharField(source='description', required=True)
    email = EmailField(required=True)

    class Meta:
        model = Contact
        fields = ("name","message","email")

