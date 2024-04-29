from django.contrib.auth.hashers import make_password
from rest_framework.serializers import ModelSerializer  # CharField can be imported here too
from rest_framework.fields import CharField#CharField should be imported here(directly)

from .user_serializers import CustomUserSerializer
from core.models import CustomUser, EmployeeProfile


class EmployeeSerializer(ModelSerializer):
    '''General Employee Serializer'''
    user = CustomUserSerializer()

    class Meta:
        model = EmployeeProfile
        fields: tuple = (
            "user",
            "skills",
            "department",
            "position"
        )
        #depth = 1


class EmployeeRegisterSerializer(ModelSerializer):
    """
    Used to Register/Create Users(Customers)
    had to follow this approach cos of forms where nested request body data is difficult/impossible
    """

    password = CharField( write_only = True, required=True, min_length=8)
    department = CharField(source="employeeprofile.department")

    def create(self, validated_data):
        profile = validated_data.pop("employeeprofile", None)
        validated_data["password"] = make_password(validated_data.get("password"))        
        user = CustomUser.objects.create(is_staff=True, **validated_data)
        EmployeeProfile.objects.create(user=user, **profile)#if signals are used. then should be removed
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
            "date_of_birth"
        )


class EmployeeUpdateSerializer(ModelSerializer):
    """
    Used to Update Users(Employee) profile
    had to follow this approach cos of forms where nested request body data is difficult
    """

    password = CharField( write_only=True, required=False, min_length=8)
    skills = CharField(source="employeeprofile.skills")
    department = CharField(source="employeeprofile.department")
    position = CharField(source="employeeprofile.position")

    def update(self, instance, validated_data):
        #extract profile details
        profile: EmployeeProfile = instance.employeeprofile
        profile_data = validated_data.pop("employeeprofile", {})
        skills = profile_data.pop("skills", profile.skills)
        department = profile_data.pop("department", profile.department)
        position = profile_data.pop("position", profile.position)

        #user instance update
        if validated_data.get("password") is not None:
            instance.set_password(validated_data["password"])
        instance.first_name = validated_data.get("first_name", instance.first_name)
        instance.last_name = validated_data.get("last_name", instance.last_name)
        instance.address = validated_data.get("address", instance.address)
        instance.image = validated_data.get("image", instance.image)
        instance.bio = validated_data.get("bio")
        instance.phone = validated_data.get("phone")
        instance.save()
        if validated_data.get("image") is not None:
            instance.process_image()

        #profile update
        profile.skills = skills
        profile.department = department
        profile.position = position
        profile.save()
        return instance

    class Meta:
        model: CustomUser = CustomUser
        fields: tuple = (
            "email", "username", "gender",
            "address", "country", "date_of_birth",
            "bio", "image", "first_name",
            "phone", "skills", "last_name",
            "department", "position",
            "avg_rating", "password",
        )
        read_only_fields = (
            "country", "gender", 
            "avg_rating", "username", "email", 
            #"position","department", "date_of_birth" # user shouldnt be able update position & dept only superusers
        )
