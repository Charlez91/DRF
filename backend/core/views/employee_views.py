from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework.status import (
    HTTP_200_OK, HTTP_201_CREATED, 
    HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN
)
from drf_spectacular.utils import extend_schema, OpenApiResponse

from core.serializers import (
    EmployeeSerializer, 
    EmployeeRegisterSerializer, 
    EmployeeUpdateSerializer
)
from core.tasks import send_update_notification


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

