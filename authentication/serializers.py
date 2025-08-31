from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer



User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['full_name', 'email', 'password']

    def create(self, validated_data):
        full_name = validated_data.get('full_name', '')

        user = User.objects.create_user(
            full_name = full_name,
            email = validated_data['email'],
            password = validated_data['password'],
            is_active = False
        )

        return user
    
        
class CreateTokenSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['full_name'] = user.full_name
        token['email'] = user.email
        token['profile_pic'] = user.profile_pic

        return token