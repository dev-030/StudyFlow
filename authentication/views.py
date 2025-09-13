from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .serializers import RegisterSerializer, CreateTokenSerializer
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.db import transaction
from .tasks import send_verification_email
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from django.http import HttpResponse
import os
from rest_framework import serializers
import secrets
from urllib.parse import urlencode
from django.shortcuts import redirect
import requests as req
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token






User = get_user_model()


class RegisterUser(APIView):
    permission_classes = [AllowAny]
    def post(self, request):

        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():

            user = serializer.save()

            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            # send_verification_email.delay(user.id, uid, token)

            return Response({"Message":"A verification mail has been sent to the email"}, status=status.HTTP_200_OK)
        return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    
class VerifyEmail(APIView):
    permission_classes = [AllowAny]
    def get(self, request, uid64, token):
        try:
            uid = urlsafe_base64_decode(uid64).decode()
            user = User.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({"error":"Invalid link"}, status=status.HTTP_400_BAD_REQUEST)

        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.profile_pic = 'https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_1280.png'
            user.save()
            return Response({"message": "Email verified successfully"}, status=200)
        return Response({"error": "Invalid or expired token"}, status=400)



class LoginUser(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({"error":"Email and password is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.filter(email=email).first()

        if not user:
            return Response({"error":"No user found with this email"}, status=status.HTTP_404_NOT_FOUND)

        user = authenticate(request, email=email, password=password)

        if user:
            refresh_token = CreateTokenSerializer.get_token(user)
            access_token = refresh_token.access_token
            
            # response = HttpResponse(status=302)
            # response["Location"] = "http://localhost:8000"

            # response.set_cookie(
            #     key="refresh_token",
            #     value=str(refresh_token),
            #     httponly=True,
            #     secure=True,
            #     samesite="Lax",
            #     max_age=60 * 60 * 24,
            #     path="/",
            #     domain="edcluster.com"
            # )

            # response.set_cookie(
            #     key="access_token",
            #     value=str(access_token),
            #     httponly=True,
            #     secure=True,
            #     samesite="Lax",
            #     max_age=60 * 60 * 24,  # 1 day
            #     path="/",
            #     domain="edcluster.com"
            # )
            # return response
            return Response({"refresh_token": str(refresh_token), "access_token": str(access_token) }, status=status.HTTP_200_OK)
        
        return Response({"error": "The user is not verified yet. Please verify the email to login"}, status=status.HTTP_400_BAD_REQUEST)
    




class GoogleLogin(APIView):
    permission_classes=[AllowAny]
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
    REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI')

    class InputSerializer(serializers.Serializer):
        code = serializers.CharField(required=True)
        error = serializers.CharField(required=False)
        state= serializers.CharField(required=True)

    def get(self, request):
        serializer = self.InputSerializer(data=request.GET)
        if not serializer.is_valid():
            state = secrets.token_urlsafe(32)
            request.session['google_oauth2_state'] = state
            params = {
                'client_id': self.GOOGLE_CLIENT_ID,
                'redirect_uri': self.REDIRECT_URI,
                'response_type': 'code',
                'scope': 'openid email profile',
                'access_type': 'offline',
                'state': state
            }

            auth_url = "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(params)
            return redirect(auth_url)
        

        code = serializer.validated_data.get('code')
        error = serializer.validated_data.get('error')
        state = serializer.validated_data.get('state')

        if error:
            return Response({"error":"Google oauth error: {error}"}, status=status.HTTP_400_BAD_REQUEST)

        session_state = request.session.get('google_oauth2_state')
        
        if not session_state:
            return Response(
                {"error": "CSRF validation failed - no session state"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        del request.session['google_oauth2_state']

        if state != session_state:
            return Response(
                {"error": "CSRF validation failed - state mismatch"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        token_data = {
            'code': code,
            'client_id': self.GOOGLE_CLIENT_ID,
            'client_secret': self.GOOGLE_CLIENT_SECRET,
            'redirect_uri': self.REDIRECT_URI,
            'grant_type': 'authorization_code'
        }

        try:
            token_response = req.post('https://oauth2.googleapis.com/token', data=token_data, timeout=10)
            token_response.raise_for_status()
            token_json = token_response.json()
        except req.RequestException as e:
            return Response({"error": f"Failed to exchange code for token: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        
        if 'error' in token_json:
            return Response({"error": f"Token exchange error: {token_json['error']}"}, status=status.HTTP_400_BAD_REQUEST)

        id_token_jwt = token_json.get('id_token')

        if not id_token_jwt:
            return Response({'error':'No Id token received'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            idinfo = id_token.verify_oauth2_token(
                id_token_jwt,
                google_requests(),
                self.GOOGLE_CLIENT_ID
            )

            email = idinfo.get('email')
            name = idinfo.get('name')
            profile_pic = idinfo.get('picture')

            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "full_name": name,
                    "is_active": True,
                    "profile_pic": profile_pic
                },
            )

            if created:
                user.is_google_auth = True
                user.save()

            refresh_token = CreateTokenSerializer.get_token(user)
            access_token = refresh_token.access_token

            response = HttpResponse(status=302)
            response["Location"] = "http://localhost:8000"

            response.set_cookie(
                key="refresh_token",
                value=str(refresh_token),
                httponly=True,
                secure=True,
                samesite="Lax",
                max_age=60 * 60 * 24,
                path="/",
                domain="edcluster.com"
            )

            response.set_cookie(
                key="access_token",
                value=str(access_token),
                httponly=True,
                secure=True,
                samesite="Lax",
                max_age=60 * 60 * 24,  # 1 day
                path="/",
                domain="edcluster.com"
            )

            return response
        except ValueError as e:
            return Response({"error": f"Invalid token: {e}"}, status=status.HTTP_400_BAD_REQUEST)

