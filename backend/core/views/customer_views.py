from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework.status import (
    HTTP_200_OK, HTTP_201_CREATED, 
    HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN
)
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiResponse

from core.serializers import (
    CustomerSerializer, 
    CustomerRegisterSerializer, 
    CustomerUpdateSerializer
)
from core.models import CustomerProfile
from core.tasks import send_activation_email
from utils.pagination import StandardResultsSetPagination


class CustomerRegisterAPIView(APIView):
    """
    Customer Registration View to register new users
    Buyer/Vendor
    """
    parser_classes: list = [FormParser, JSONParser]
    #serializer_class = CustomerRegisterSerializer #no need for this. serializer_class field/get_serializer method not in APIView parent class.

    @extend_schema(
        summary='Customer User Registration',
        description="This is POST method api, in which user data will be created and through signals tokens created as well",
        request= CustomerRegisterSerializer,
        responses={
            200: OpenApiResponse(description='Json Response'),
            400: OpenApiResponse(description='Validation error')
        }
    )

    def post(self, request):
        #user_serializer = CustomUserSerializer(data=request.data)
        serializer = CustomerRegisterSerializer(data = request.data)
        if serializer.is_valid():
            user = serializer.save()
            current_site = get_current_site(request)
            send_activation_email.delay(current_site, user)
            return Response({"message":"User Registered Successfully. Activation Email Sent", 
                             "data":serializer.data}, HTTP_201_CREATED)
        return Response(serializer.errors, HTTP_400_BAD_REQUEST)


class CustomerUpdateAPIView(APIView):#testing between using APIVIEW or genericviewset
    """
    Customer Update/Get Profile Details  View 
    """
    parser_classes: list = [MultiPartParser, FormParser, JSONParser]
    permission_classes = (IsAuthenticated,)
    throttle_classes = (ScopedRateThrottle,)#will review and maybe refactor cos of the get method which might receive more calls than a patch
    throttle_scope = "profile"
    #serializer_class = UserRegisterSerializer #no need for this. serializer_class field/get_serializer method not in APIView parent class.

    @extend_schema(
        summary='Profile Update',
        description="This is Patch method api, in which user data will be updated",
        request= CustomerUpdateSerializer,
        responses={
            200: OpenApiResponse(description='Json Response'),
            400: OpenApiResponse(description='Validation error')
        }
    )

    def get(self, request):
        serializer = CustomerSerializer(instance=request.user.customerprofile)
        return Response(serializer.data, HTTP_200_OK)
    
    def patch(self, request):
        instance = request.user
        serializer = CustomerUpdateSerializer(instance=instance, data=request.data, 
                                            partial= True)
        if instance.is_staff==True:
            return Response({"error":"NOT ALLOWED. Only Customers can update their details"},
                            status=HTTP_403_FORBIDDEN)
        if serializer.is_valid():
            print(serializer.validated_data)
            serializer.save()
            #send_update_notification.delay(instance.username, instance.email)
            return Response(serializer.data, HTTP_200_OK)
        return Response(serializer.errors, HTTP_400_BAD_REQUEST)

class CustomerRetrieveView(APIView):
    """
    Customer Retrieve route view for getting a customer profile
    Buyers/Vendors alike
    """
    def get(self, request, username):
        instance = get_object_or_404(CustomerProfile, user__username=username)
        serializer = CustomerSerializer(instance=instance)
        return Response(serializer.data, HTTP_200_OK)


class CustomerListView(ListAPIView):
    """
    Customer List routes view for listing all customers
    Buyers/Vendors alike
    """
    serializer_class = CustomerSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["user_type"]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        queryset = CustomerProfile.objects.filter(user__email_verified=True).all()
        return queryset
