from django.shortcuts import redirect
from rest_framework import generics, status, views, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.http import HttpResponsePermanentRedirect
# from django.contrib.auth import get_user_model
import jwt
import os

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .serializers import (
    RegisterSerializer, EmailVerificationSerializer, LoginSerializer,
    SetNewPasswordSerializer, ResetPasswordEmailRequestSerializer, LogoutSerializer
)
from .models import User
from .utils import Util
from .renderers import UserRenderer


class CustomRedirect(HttpResponsePermanentRedirect):
    allowed_schemes = [os.environ.get('APP_SCHEME'), 'http', 'https']


class RegisterView(generics.GenericAPIView):
    serializer_class = RegisterSerializer
    renderer_classes = (UserRenderer,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user_data = serializer.data
        user = User.objects.get(email=user_data['email'])

        token = RefreshToken.for_user(user).access_token
        current_site = get_current_site(request).domain
        relative_link = reverse('email-verify')
        absurl = f'http://{current_site}{relative_link}?token={token}'
        email_body = f'Hi {user.username}, Use the link below to verify your email \n{absurl}'

        data = {
            'email_body': email_body,
            'to_email': user.email,
            'email_subject': 'Verify your email'
        }

        Util.send_email(data)
        return Response(user_data, status=status.HTTP_201_CREATED)


class VerifyEmail(views.APIView):
    serializer_class = EmailVerificationSerializer

    token_param_config = openapi.Parameter(
        'token', in_=openapi.IN_QUERY, description='Token for email verification', type=openapi.TYPE_STRING
    )

    @swagger_auto_schema(manual_parameters=[token_param_config])
    def get(self, request):
        token = request.GET.get('token')
        if not token:
            return Response({'error': 'Token is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user = User.objects.get(id=payload['user_id'])
            if not user.is_verified:
                user.is_verified = True
                user.save()
            return Response({'email': 'Successfully activated'}, status=status.HTTP_200_OK)
        
        except jwt.ExpiredSignatureError:
            return Response({'error': 'Activation link has expired'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.DecodeError:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


class LoginAPIView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RequestPasswordResetEmail(generics.GenericAPIView):
    serializer_class = ResetPasswordEmailRequestSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        email = request.data.get('email', '')

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            # encodes the user id
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            # take care of knowing if a user has changed the password to avoid conflicts
            token = PasswordResetTokenGenerator().make_token(user)
            current_site = get_current_site(request=request).domain
            relative_link = reverse('password-reset-confirm', kwargs={'uidb64': uidb64, 'token': token})
            redirect_url = request.data.get('redirect_url', '')
            absurl = f'http://{current_site}{relative_link}?redirect_url={redirect_url}'
            email_body = f'Hello, \n Use the link below to reset your password  \n{absurl}'
            data = {
                'email_body': email_body,
                'to_email': user.email,
                'email_subject': 'Reset your password'
            }
            Util.send_email(data)
        return Response({'success': 'We have sent you a link to reset your password'}, status=status.HTTP_200_OK)

# get request to validate user
class PasswordTokenCheckAPI(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def get(self, request, uidb64, token):
        redirect_url = request.GET.get('redirect_url')

        try:
            # get which user it is
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)

            # check if the user has used his token
            if not PasswordResetTokenGenerator().check_token(user, token):
                # return CustomRedirect(f'{redirect_url}?token_valid=False' if redirect_url else f'{os.environ.get("FRONTEND_URL", "")}?token_valid=False')
                return Response({'error': 'Token is not valid, please request a new one'})
            
            return Response({'success': True, 'message': 'Credentials valid', 'uidb64': uidb64, 'token': token}, status =status.HTTP_200_OK)

            # return CustomRedirect(f'{redirect_url}?token_valid=True&message=Credentials Valid&uidb64={uidb64}&token={token}' if redirect_url else f'{os.environ.get("FRONTEND_URL", "")}?token_valid=False')

        # if user has tampered with the token
        except DjangoUnicodeDecodeError:
            return CustomRedirect(f'{redirect_url}?token_valid=False' if redirect_url else f'{os.environ.get("FRONTEND_URL", "")}?token_valid=False')
        except User.DoesNotExist:
            return Response({'error': 'Token is not valid, please request a new one'}, status=status.HTTP_400_BAD_REQUEST)


class SetNewPasswordAPIView(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'success': True, 'message': 'Password reset success'}, status=status.HTTP_200_OK)


class LogoutAPIView(generics.GenericAPIView):
    serializer_class = LogoutSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
