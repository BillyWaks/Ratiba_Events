# authentication/middleware.py
from django.http import JsonResponse
from django.utils import timezone
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.tokens import RefreshToken

class TokenValidationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Extract token from the Authorization header
        auth = request.headers.get('Authorization', None)
        if auth and auth.startswith("Bearer "):
            try:
                # Extract and validate the token
                token = auth.split(' ')[1]
                jwt_auth = JWTAuthentication()
                validated_token = jwt_auth.get_validated_token(token)
                
                # Set the user on the request
                request.user = jwt_auth.get_user(validated_token)
                
                # Check remaining time on the token; refresh if it's close to expiring
                expiration_timestamp = validated_token['exp']
                time_remaining = expiration_timestamp - timezone.now().timestamp()

                if time_remaining < 300:  # If less than 5 minutes left
                    refresh = RefreshToken.for_user(request.user)
                    # Refresh token and set a new access token in the response
                    response = self.get_response(request)
                    response['Authorization'] = f'Bearer {refresh.access_token}'
                    return response

            except (TokenError, InvalidToken):
                return JsonResponse({'detail': 'Token is invalid or expired.'}, status=401)

        # Allow request to proceed if no token is present; DRF will enforce permissions
        response = self.get_response(request)
        return response
