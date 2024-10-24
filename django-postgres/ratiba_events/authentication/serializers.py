from rest_framework import serializers
from .models import User
from django.contrib import auth
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
import logging


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)
    first_name = serializers.CharField(max_length=255, required=True)
    last_name = serializers.CharField(max_length=255, required=True)

    default_error_messages = {
        'username': 'The username should only contain alphanumeric characters'}

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password']

    def validate(self, attrs):
        email = attrs.get('email', '')
        username = attrs.get('username', '')

        if not username.isalnum():
            raise serializers.ValidationError(
                'The username should only contain alphanumeric characters'
            )
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

class EmailVerificationSerializer(serializers.ModelSerializer):
    token = serializers.CharField(max_length=602)

    class Meta:
        model = User
        fields = ['token']


class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255, min_length=3)
    password = serializers.CharField(
        max_length=68, min_length=6, write_only=True)
    username = serializers.CharField(
        max_length=255, min_length=3, read_only=True)

    tokens = serializers.SerializerMethodField()

    def get_tokens(self, obj):
        user = User.objects.get(email=obj['email'])

        return {
            'refresh': user.tokens()['refresh'],
            'access': user.tokens()['access']
        }

    class Meta:
        model = User
        fields = ['email', 'password', 'username', 'tokens']

# validates login
    def validate(self, attrs):
        email = attrs.get('email', '')
        password = attrs.get('password', '')
        filtered_user_by_email = User.objects.filter(email=email)
        user = auth.authenticate(email=email, password=password)

        if filtered_user_by_email.exists() and filtered_user_by_email[0].auth_provider != 'email':
            raise AuthenticationFailed(
                detail='Please continue your login using ' + filtered_user_by_email[0].auth_provider)

        if not user:
            raise AuthenticationFailed('Invalid credentials, try again')
        if not user.is_active:
            raise AuthenticationFailed('Account disabled, contact admin')
        if not user.is_verified:
            raise AuthenticationFailed('Email is not verified')

        return {
            'email': user.email,
            'username': user.username,
            'tokens': user.tokens
        }
          # The following line will never be reached, so it should be removed
        return super().validate(attrs)


class ResetPasswordEmailRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=2)

    redirect_url = serializers.CharField(max_length=500, required=False)

    class Meta:
        fields = ['email']


logger = logging.getLogger(__name__)

class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(min_length=6, max_length=68, write_only=True)
    token = serializers.CharField(min_length=1, write_only=True)
    uidb64 = serializers.CharField(min_length=1, write_only=True)

    class Meta:
        fields = ['password', 'token', 'uidb64']

    def validate(self, attrs):
        """Validates the reset password request."""
        password = attrs.get('password')
        token = attrs.get('token')
        uidb64 = attrs.get('uidb64')

        try:
            # Decode the user ID
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=user_id)

            # Check if the token is valid
            if not PasswordResetTokenGenerator().check_token(user, token):
                logger.error('Invalid token for user ID %s', user_id)
                raise AuthenticationFailed('The reset link is invalid', 401)

        except User.DoesNotExist:
            logger.error('User not found for ID %s', user_id)
            raise AuthenticationFailed('User not found', 404)
        except Exception as e:
            logger.exception('Exception during token validation for user ID %s: %s', user_id, str(e))
            raise AuthenticationFailed('The reset link is invalid', 401)

        attrs['user'] = user
        return attrs

    def save(self, **kwargs):
        """Sets the new password for the user."""
        password = self.validated_data['password']
        user = self.validated_data['user']

        user.set_password(password)
        user.save()

        return user



class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    default_error_message = {
        'bad_token': ('Token is expired or invalid')
    }

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs

    def save(self, **kwargs):

        try:
            RefreshToken(self.token).blacklist()

        except TokenError:
            self.fail('bad_token')


# class RegisterSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(
#         max_length=68, min_length=6, write_only=True)

#     default_error_messages = {
#         'username': 'The username should only contain alphanumeric characters'}

#     class Meta:
#         model = User
#         fields = ['email', 'username', 'password']

#     def validate(self, attrs):
#         email = attrs.get('email', '')
#         username = attrs.get('username', '')

#         if not username.isalnum():
#             raise serializers.ValidationError(
#                 'The username should only contain alphanumeric characters'
#             )
#                 # self.default_error_messages)
#         return attrs

#     def create(self, validated_data):
#         return User.objects.create_user(**validated_data)
