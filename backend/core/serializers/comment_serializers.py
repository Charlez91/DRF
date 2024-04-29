from rest_framework.serializers import ModelSerializer  # CharField can be imported here too
from rest_framework.exceptions import ValidationError
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework_json_api.serializers import PrimaryKeyRelatedField

from core.models import CustomUser, Comment
from ecommerce.models import Item


class CommentSerializer(ModelSerializer):
    """
    Serializer for comment viewset
    """
    vendor = PrimaryKeyRelatedField(queryset=CustomUser.objects.all())#might use select-related later
    item = PrimaryKeyRelatedField(queryset=Item.objects.all(), required=False)#might use select-related later

    class Meta:
        model = Comment
        fields = ("name", "email", "comment", "rating", "item", "vendor")
    
    def validate_rating(self, value):
        '''
        validates `comment.rating` field
        '''
        print("validating rating", type(value))
        if value < 1 or value > 5:
            raise ValidationError("Rating Value must be between 1 and 5")
        return value

    def validate(self, attrs:dict):
        '''
        validates the data sent to the serializer
        prevents user from rating himself
        '''
        rater_email: str = attrs.get("email")
        vendor: CustomUser = attrs.get("vendor")
        if vendor.email == rater_email:
            raise ValidationError("Scammer wan rate himself. Not allowed", HTTP_400_BAD_REQUEST)
        #might later implement algorithm to prevent multiple ratings from a user name/email
        return attrs
    
