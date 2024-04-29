from rest_framework.serializers import ModelSerializer  # CharField can be imported here too

from core.models import CustomUser

class CustomUserSerializer(ModelSerializer):

    class Meta:
        model = CustomUser
        fields: tuple = (
            "username","email",
            "gender","bio","avg_rating",
            "date_of_birth",
            "phone","address",
            "country","image",
        )
