from json import JSONDecodeError

from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser, FormParser
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .serializers import ContactSerializer, UserRegisterSerializer

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
                return Response(serializer.data)
            else:
                return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
        except JSONDecodeError:
            return JsonResponse({'result':'error', 'message':'Json Decoding Error'}, status=400)


class RegisterAPIView(APIView):
    """
    User Registration View to register new users
    """
    parser_classes: list = [FormParser, JSONParser]
    #serializer_class = UserRegisterSerializer #no need for this. serializer_class field/get_serializer method not in APIView parent class.

    @extend_schema(
        summary='User Registration',
        description="This is POST method api, in which user data will be created and through signals tokens created as well",
        request= UserRegisterSerializer,
        responses={
            200: OpenApiResponse(description='Json Response'),
            400: OpenApiResponse(description='Validation error')
        }
    )

    def Post(self, request):
        serializer = UserRegisterSerializer(data = request.data)
        if serializer.is_valid(raise_exception=True):
            print(serializer.validated_data) #to view the validated data object/dict
            serializer.save()
            return Response({"message":"User Registered Successfully", "data":serializer.data}, HTTP_200_OK)
        return Response(serializer.errors, HTTP_400_BAD_REQUEST)

