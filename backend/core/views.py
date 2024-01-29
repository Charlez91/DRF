from json import JSONDecodeError

from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.status import (
    HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST
    )
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import (
    ListModelMixin, RetrieveModelMixin, 
    CreateModelMixin, DestroyModelMixin,
    )
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .serializers import (ContactSerializer, 
                          CustomerSerializer, 
                          CustomUserSerializer, 
                          EmployeeSerializer,
                          CustomerRegisterSerializer,
                          CustomerUpdateSerializer,
                          EmployeeRegisterSerializer,
                          CommentSerializer
                          )
from .models import Comment


# Create your views here.
class ContactAPIView(APIView):
    '''
    The contact routes view class implementation
    for creating contact entries
    '''
    serializer_class = ContactSerializer
    #parser_classes = [JSONParser]
    
    def get_serializer_context(self):
        return {
            'request':self.request,
            'format': self.format_kwarg,
            'view':self
            }

    def get_serializer(self, *args, **kwargs):
        kwargs['context'] = self.get_serializer_context()
        return self.serializer_class(*args, **kwargs)
    
    def post(self, request):
        try:
            data = JSONParser().parse(request)
            serializer = ContactSerializer(data=data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                #implement email sending algorithm here or in models or in serializer celery inclusive
                return Response(serializer.data)
            else:
                return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
        except JSONDecodeError:
            return JsonResponse({'result':'error', 'message':'Json Decoding Error'}, status=400)


class CustomerRegisterAPIView(APIView):
    """
    Customer Registration View to register new users
    Buyer/Vendor
    """
    parser_classes: list = [FormParser, JSONParser]
    #serializer_class = UserRegisterSerializer #no need for this. serializer_class field/get_serializer method not in APIView parent class.

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
            print(serializer.validated_data, serializer.data) #to view the validated data object/dict
            #serializer.save()
            return Response({"message":"User Registered Successfully", "data":serializer.data}, HTTP_201_CREATED)
        return Response(serializer.errors, HTTP_400_BAD_REQUEST)


class CustomerUpdateAPIView(APIView):#testing between using APIVIEW or genericviewset
    """
    Customer Update/Get Profile Details  View 
    """
    parser_classes: list = [MultiPartParser, JSONParser]
    permission_classes = (IsAuthenticated,)
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
        serializer = CustomerSerializer(instance=request.user)
        serializer.is_valid(raise_exception=True)#just for tests. NOT NEEDED
        return Response(serializer.data, HTTP_200_OK)
    
    def patch(self, request):
        serializer = CustomerUpdateSerializer(instance=request.user.customerprofile, 
                                              data=request.data, files=request.files, partial= True)
        if serializer.is_valid(raise_exception=True):
            #serializer.save()
            return Response(serializer.data, HTTP_200_OK)
        return Response(serializer.errors, HTTP_400_BAD_REQUEST)



class EmployeerRegisterAPIView(APIView):
    """
    User Registration View to register new users
    """
    parser_classes: list = [FormParser, JSONParser]
    permission_classes = (IsAuthenticated,)
    #serializer_class = UserRegisterSerializer #no need for this. serializer_class field/get_serializer method not in APIView parent class.

    @extend_schema(
        summary='Employee User Registration',
        description="This is POST method api, in which user data will be created and through signals tokens created as well",
        request= CustomerRegisterSerializer,
        responses={
            200: OpenApiResponse(description='Json Response'),
            400: OpenApiResponse(description='Validation error')
        }
    )

    def post(self, request):
        serializer = EmployeeRegisterSerializer(data = request.data)
        if serializer.is_valid() and request.user.is_staff:
            print(serializer.validated_data, serializer.data) #to view the validated data object/dict
            #serializer.save()
            return Response({"message":"Employee User Registered Successfully", 
                             "data":serializer.data}, HTTP_201_CREATED)
        return Response(serializer.errors, HTTP_400_BAD_REQUEST)


class CommentViewset(ListModelMixin, CreateModelMixin, 
                        RetrieveModelMixin, DestroyModelMixin, GenericViewSet):
    """
    the Comment Route's viewset class implementation
    for adding comments/ratings on vendors
    """
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticated,)
    filterset_fields = ["approved", "email", "rating"]
    search_fields = ["email", "vendor__email", "comment"]
    ordering_fields = ["email", "date_created"]
    ordering = ["-date_created"]

    def get_queryset(self):
        return Comment.objects.filter(user=self.request.user)
