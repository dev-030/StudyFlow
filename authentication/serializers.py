from rest_framework import serializers
from django.contrib.auth import get_user_model



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
    
        