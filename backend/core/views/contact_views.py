from json import JSONDecodeError

from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework.status import HTTP_400_BAD_REQUEST
from drf_spectacular.utils import extend_schema, OpenApiResponse

from core.serializers import ContactSerializer


class ContactAPIView(APIView):
    '''
    The contact routes view class implementation
    for creating contact entries
    '''
    serializer_class = ContactSerializer
    throttle_classes = [ScopedRateThrottle,]
    throttle_scope = "contact"

    @extend_schema(
        summary='Contact Admin View',
        description="This is POST method api, in which contact messages can be dropped for website admins",
        request= ContactSerializer,
        responses={
            200: OpenApiResponse(description='Json Response'),
            400: OpenApiResponse(description='Validation error')
        }
    )

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
            serializer = self.get_serializer(data=data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                #implement email sending algorithm here or in models or in serializer celery inclusive
                return Response(serializer.data)
            else:
                return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
        except JSONDecodeError:
            return JsonResponse({'result':'error', 'message':'Json Decoding Error'}, status=400)
