from django.contrib.sites.shortcuts import get_current_site
from django.views.generic import View
from django.contrib import messages
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.status import HTTP_200_OK
from drf_spectacular.utils import extend_schema, OpenApiResponse

from core.models import CustomUser
from core.tasks import send_activation_email
from ..core_utils.token import account_activation_token


class EmailVerificationView(APIView):
    """
    View to check if a user's email is verified
    Sends verification email if False
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.email_verified == False:
            current_site = get_current_site(request)#refactored because of the difficulty in serializer the user object to celery task decorated functions
            send_activation_email(current_site, user)#would wrap in try-except block to handle email sending errors
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


