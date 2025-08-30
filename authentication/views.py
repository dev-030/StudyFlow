from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .serializers import RegisterSerializer
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




User = get_user_model()


class RegisterUser(APIView):
    permission_classes = [AllowAny]
    def post(self, request):

        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():

            user = serializer.save()

            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            send_verification_email.delay(user.id, uid, token)

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
            user.save()
            return Response({"message": "Email verified successfully"}, status=200)
        return Response({"error": "Invalid or expired token"}, status=400)



class LoginUser(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or password:
            return Response({"error":"Email and password is required"}, status=status.HTTP_400_BAD_REQUEST)
        user = authenticate(request, email=email, password=password)

        if user:
            return Response({"message":"This is success"}, status=status.HTTP_200_OK)
        return Response({"message": "this is an error"}, status=status.HTTP_400_BAD_REQUEST)



# class GoogleLogin(APIView):








