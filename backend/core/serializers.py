from django.contrib.auth.models import User
from rest_framework.serializers import ModelSerializer  # CharField can be imported here too
from rest_framework.fields import CharField, EmailField #CharField can be imported too

from .models import Contact

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


class UserRegisterSerializer(ModelSerializer):
    """
    Used to Register/Create Users
    """

    password = CharField(
        #write_only=True,
        required=True,
    )

    class Meta:
        model: User = User
        fields: tuple = (
            "email",
            "username",
            "password",
        )

