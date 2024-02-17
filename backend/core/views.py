from json import JSONDecodeError

from django.http import JsonResponse
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import render, get_object_or_404
from django.views.generic import View
from django.contrib import messages
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from rest_framework.status import (
    HTTP_200_OK, HTTP_201_CREATED, 
    HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN
    )
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.generics import ListAPIView
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
                          EmployeeSerializer, 
                          EmployeeUpdateSerializer,
                          CustomerRegisterSerializer,
                          CustomerUpdateSerializer,
                          EmployeeRegisterSerializer,
                          CommentSerializer
                          )
from .models import Comment, CustomUser, CustomerProfile
from .tasks import send_activation_email, send_update_notification
from .token import account_activation_token


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
            #print(serializer.validated_data, serializer.data) #to view the validated data object/dict
            user = serializer.save()
            send_activation_email.delay(request, user)
            return Response({"message":"User Registered Successfully. Activation Email Sent", 
                             "data":serializer.data}, HTTP_201_CREATED)
        return Response(serializer.errors, HTTP_400_BAD_REQUEST)


class CustomerUpdateAPIView(APIView):#testing between using APIVIEW or genericviewset
    """
    Customer Update/Get Profile Details  View 
    """
    parser_classes: list = [MultiPartParser, FormParser, JSONParser]
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
    #paginator = []
    
    def get_queryset(self):
        queryset = CustomerProfile.objects.filter(user__email_verified=True)
        return queryset

class EmployeerAPIView(APIView):
    """
    User Registration View to register new users
    """
    parser_classes: list = [MultiPartParser, FormParser, JSONParser]
    permission_classes = (IsAuthenticated,)
    #serializer_class = UserRegisterSerializer #no need for this. serializer_class field/get_serializer method not in APIView parent class.

    @extend_schema(
        summary='Employee User Registration',
        description="This is POST method api, in which user data will be created and through signals tokens created as well",
        request= EmployeeUpdateSerializer,
        responses={
            200: OpenApiResponse(description='Json Response'),
            400: OpenApiResponse(description='Validation error')
        }
    )

    def post(self, request):
        serializer = EmployeeRegisterSerializer(data = request.data)
        if serializer.is_valid() and request.user.is_staff:#only staffs can register staff
            #print(serializer.validated_data, serializer.data) #to view the validated data object/dict
            serializer.save()
            return Response({"message":"Employee User Registered Successfully", 
                             "data":serializer.data}, HTTP_201_CREATED)
        return Response(serializer.errors, HTTP_400_BAD_REQUEST)
    
    
    def get(self, request):
        serializer = EmployeeSerializer(instance=request.user.employeeprofile)
        return Response(serializer.data, HTTP_200_OK)
    
    def patch(self, request):
        instance = request.user
        serializer = EmployeeUpdateSerializer(instance=instance, data=request.data, 
                                             partial= True)
        try:
            if instance.is_staff==False and instance.employeeprofile:
                return Response({"error":"NOT ALLOWED. Only Staff can update their details via dis link"},
                                    status=HTTP_403_FORBIDDEN)
        except:
            return Response({"error":"profile does not exist"}, HTTP_400_BAD_REQUEST)
        if serializer.is_valid(raise_exception=True):
            print(serializer.validated_data)
            serializer.save()
            send_update_notification(instance.username, instance.email)
            return Response(serializer.data, HTTP_200_OK)
        return Response(serializer.errors, HTTP_400_BAD_REQUEST)


class EmailVerificationView(APIView):
    """
    View to check if a user's email is verified
    Sends verification email if False
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.email_verified == False:
            send_activation_email.delay(request, user)#would wrap in try-except block to handle email sending errors
            return Response({"message": "Verification Email Sent successfully"}, HTTP_200_OK)
        return Response({"message":"User's Email Has already been verified"}, HTTP_200_OK)


class ActivateView(View):
    """
    View for Email Activation logic
    Opens from verification mail
    """

    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            user = None

        if user is not None and account_activation_token.check_token(user,
                                                                     token):
            #user.is_active = True #for now disabled
            user.email_verified = True
            user.save()

            username = user.username

            messages.success(request, f"Congratulations {username} !!! "
                                      f"Your account was created and activated "
                                      f"successfully"
                             )

            return render(request=request, template_name='core/account_activation_valid.html')
        else:
            return render(request, 'core/account_activation_invalid.html')



class CommentViewset(ListModelMixin, CreateModelMixin, 
                        RetrieveModelMixin, DestroyModelMixin, GenericViewSet):
    """
    the Comment Route's viewset class implementation
    for adding comments/ratings on vendors
    """
    serializer_class = CommentSerializer
    parser_classes = [JSONParser, FormParser]
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["email", "rating", "vendor__username", "item_id"]
    search_fields = ["item__id", "comment"]
    ordering_fields = ["email", "date_created"]
    ordering = ["-date_created"]
    queryset = Comment.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = CommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if serializer.data.get("email") == request.user.email:
        #prevent another user from commenting on another 
            return super().create(request, *args, **kwargs)
        return Response({'message':"Not Allowed. Commenter email and signed in users email must match", 
                         "status":"Failed"}, status=HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk, *args, **kwargs):
        obj = get_object_or_404(Comment, pk=pk)
        if request.user.email == obj.email:
            super().destroy(request, *args, **kwargs)
            return Response({"message":"Message deleted successfully", "status":"success"})
        return Response({"message":"comment can only be deleted by the creator/'commenter'."}, status=HTTP_403_FORBIDDEN)
