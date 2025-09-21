from rest_framework import serializers
from .models import Class
import re
from django.db import transaction
from organizations.models import Membership



class ClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = ["id", "name", "description", "classroom", "created_at"]
        read_only_fields = ["id", "created_at"]
        
    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Name is required")
        if len(value) > 100:
            raise serializers.ValidationError("Name too long")
        if not re.fullmatch(r"[A-Za-z0-9\s\-]+", value):
            raise serializers.ValidationError("Invalid characters in name")
        return value
    
    def create(self, validated_data):
        request = self.context['request']
        validated_data['admin'] = request.user

        print(validated_data)

        if validated_data.get('classroom') and validated_data.get('classroom').admin != request.user:
            validated_data['classroom'] = None

        print(validated_data)

        try:
            with transaction.atomic():
                cls = Class.objects.create(**validated_data)
                Membership.objects.create(
                    user = request.user,
                    classes = cls,
                    role = 'admin',
                    status = 'approved'
                )
        except Exception as e :
            raise serializers.ValidationError({'error': str(e)})
        return cls