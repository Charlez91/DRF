from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from rest_framework.serializers import ModelSerializer  # CharField can be imported here too
from rest_framework.exceptions import ValidationError
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK
from rest_framework.fields import (
    CharField, EmailField, 
    DecimalField, URLField, 
    ) #CharField should be imported here(directly)
from rest_framework_json_api.serializers import PrimaryKeyRelatedField

from .models import (Contact, CustomUser, CustomerProfile, EmployeeProfile, Comment)


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


class CustomerRegisterSerializer(ModelSerializer):
    """
    Serializer class for Register/Create Users(Customers) view
    had to follow this approach cos of forms where nested request body data is difficult/impossible
    would have used nested serializer relations
    """

    password = CharField( write_only = True  , required=True, min_length=8)
    user_type = CharField(source="customerprofile.user_type")

    def create(self, validated_data):
        user_type = validated_data.pop("user_type")
        validated_data["password"] = make_password(validated_data.get("password"))
        user = CustomUser.objects.create(**validated_data)
        CustomerProfile.objects.create(user=user, user_type=user_type)
        #implement algorithm to send email on registration
        return user

    class Meta:
        model: CustomUser = CustomUser
        fields: tuple = (
            "email",
            "username",
            "password",
            "address",
            "country",
            "gender",
            "phone",
            "user_type",
        )


class EmployeeRegisterSerializer(ModelSerializer):
    """
    Used to Register/Create Users(Customers)
    had to follow this approach cos of forms where nested request body data is difficult/impossible
    """

    password = CharField( write_only = True, required=True, min_length=8)
    department = CharField(source="employeeprofile.department")

    def create(self, validated_data):
        department = validated_data.pop("department", None)
        validated_data["password"] = make_password(validated_data.get("password"))        
        user = CustomUser.objects.create(is_staff=True, **validated_data)
        EmployeeProfile.objects.create(user=user, department= department)#if signals are used. then should be removed
        #implement algorithm to send email on registeration
        return user

    class Meta:
        model: CustomUser = CustomUser
        fields: tuple = (
            "email",
            "username",
            "address",
            "country",
            "password",
            "gender",
            "phone",
            "department",
        )


class CustomerUpdateSerializer(ModelSerializer):
    """
    Used to Update Users(Customers) profile
    had to follow this approach cos of forms where nested request body data is difficult
    """

    password = CharField( write_only=True, required=False, min_length=8)
    user_type = CharField(source="customerprofile.user_type")
    store_address = CharField(source="customerprofile.store_address")
    store_url = URLField(source="customerprofile.store_url")
    avg_rating = DecimalField(source="customerprofile.avg_rating", max_digits=4, decimal_places=2)
    
    def update(self, instance, validated_data):
        profile: CustomerProfile = instance.customerprofile
        store_address = validated_data.pop("store_address", profile.store_address)
        store_url = validated_data.pop("store_url", profile.store_url)

        #user instance update
        if validated_data.get("password") != None:
            instance.set_password(validated_data["password"])
        instance.first_name = validated_data.get("first_name", instance.first_name)
        instance.last_name = validated_data.get("last_name", instance.last_name)
        instance.address = validated_data.get("address", instance.address)
        instance.image = validated_data.get("image", instance.image)
        instance.bio = validated_data.get("bio")
        instance.phone = validated_data.get("phone")
        instance.save()
        #implement algorithm for sending email on instance update

        #profile update
        profile.store_address = store_address
        profile.store_url = store_url
        profile.save()
        return instance

    class Meta:
        model: CustomUser = CustomUser
        fields: tuple = (
            "email", "username", "gender",
            "address", "country",
            "bio", "image", "first_name",
            "phone", "user_type", "last_name",
            "store_address", "store_url",
            "avg_rating",
        )
        read_only_fields = (
            "country", "gender", 
            "avg_rating", "user_type", 
            "username", "email", "gender"
        )


class CustomUserSerializer(ModelSerializer):

    class Meta:
        model = CustomUser
        fields: tuple = (
            "username",
            "email",
            "Country",
        )


class EmployeeSerializer(ModelSerializer):

    user = CustomUserSerializer()

    class Meta:
        model = EmployeeProfile
        fields: tuple = (
            "user",
            "skills",
            "department",
        )
    

class CustomerSerializer(ModelSerializer):

    user = CustomUserSerializer()

    class Meta:
        model = CustomerProfile
        fields: tuple = (
            "user",
            "user_type",
        )


class CommentSerializer(ModelSerializer):
    """
    Serializer for comment viewset
    """
    vendor = PrimaryKeyRelatedField(queryset=CustomUser.objects.all())#might use select-related later

    class Meta:
        model = Comment
        field = ("name", "email", "comment", "rating", "vendor")
    
    def validate_rating(self, value):
        '''
        validates `comment.rating` field
        '''
        value = float(value)
        if value < 1 and value > 5:
            raise ValidationError("Value must be between 1 and 5")
        #implement algorithm for decimal places
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
    
