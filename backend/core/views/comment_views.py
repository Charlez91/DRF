from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser, FormParser
from rest_framework.status import (
    HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN
)
from rest_framework.mixins import (
    ListModelMixin, RetrieveModelMixin, 
    CreateModelMixin, DestroyModelMixin,
    )
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiResponse

from core.serializers import (
    CommentSerializer,
)
from core.models import Comment


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

    @extend_schema(
        summary='Comment View',
        description="This method contains method to retrieve, create, update and delete comments on a User",
        request= CommentSerializer,
        responses={
            200: OpenApiResponse(description='Json Response'),
            400: OpenApiResponse(description='Validation error')
        }
    )

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
