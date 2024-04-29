from django.contrib.auth.hashers import make_password
from rest_framework.serializers import ModelSerializer  # CharField can be imported here too
from rest_framework.fields import (
    CharField,  URLField,
    ) #CharField should be imported here(directly)

from .user_serializers import CustomUserSerializer
from core.tasks import del_prev_image
from core.models import CustomUser, CustomerProfile


class CustomerSerializer(ModelSerializer):
    """
    General Customer Serializer class
    """
    user = CustomUserSerializer()

    class Meta:
        model = CustomerProfile
        fields: tuple = (
            "user",
            "user_type",
            "store_address",
            "store_url"
        )



class CustomerRegisterSerializer(ModelSerializer):
    """
    Serializer class for Register/Create Users(Customers) view
    had to follow this approach cos of forms where nested request body data is difficult/impossible
    would have used nested serializer relations
    """

    password = CharField( write_only = True  , required=True, min_length=8)
    user_type = CharField(source="customerprofile.user_type")

    def create(self, validated_data):
        print(validated_data)
        profile = validated_data.pop("customerprofile")
        validated_data["password"] = make_password(validated_data.get("password"))
        #user = CustomUser.objects.create(is_active= False, **validated_data)
        user = CustomUser.objects.create(**validated_data)
        #if signals are used for profile creation, dis is not needed
        CustomerProfile.objects.create(user=user, **profile)
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
            "date_of_birth"
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
    
    def update(self, instance, validated_data):
        profile: CustomerProfile = instance.customerprofile
        profile_data = validated_data.pop("customerprofile", {}) #wrap in try except block
        store_address = profile_data.pop("store_address", profile.store_address)
        store_url = profile_data.pop("store_url", profile.store_url)

        #user instance update
        old_image = instance.image
        if validated_data.get("password") != None:
            instance.set_password(validated_data["password"])
        instance.first_name = validated_data.get("first_name", instance.first_name)
        instance.last_name = validated_data.get("last_name", instance.last_name)
        instance.address = validated_data.get("address", instance.address)
        instance.image = validated_data.get("image", instance.image)#might introduce a way of hashing old images and comparing with new ones to know when a new image is uploaded
        instance.bio = validated_data.get("bio")
        instance.phone = validated_data.get("phone")
        instance.save()
        if validated_data.get("image") is not None:
            instance.process_image()
            print("old image",old_image, "path", old_image.path)
            if "default"  not in old_image:
                del_prev_image.delay(old_image.path)
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
            "address", "country", "date_of_birth",
            "bio", "image", "first_name",
            "phone", "user_type", "last_name",
            "store_address", "store_url",
            "avg_rating","password",
        )
        read_only_fields = (
            "country", "gender", 
            "avg_rating", "user_type", 
            "username", "email","date_of_birth",
        )

