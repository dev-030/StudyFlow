from rest_framework import serializers
from .models import Classroom
import re
from django.db import transaction
from organizations.models import Membership, Organization
from classes.models import Class




class ClassesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = ["id", "name", "description", "created_at"]



class ClassroomSerializer(serializers.ModelSerializer):
    role = serializers.CharField(read_only=True)
    student_count = serializers.IntegerField(read_only=True)
    organization_name = serializers.CharField(read_only=True)
    classes = ClassesSerializer(read_only=True, many=True)
    class Meta:
        model = Classroom
        fields = ["id", "name", "description", "organization", "created_at", "role", "student_count", "organization_name", "classes"]
        read_only_fileds = ["id", "description", "organization", "created_at", "role", "student_count", "organization_name", "classes"]

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

        if validated_data.get('organization') and validated_data.get('organization').created_by != request.user:
            validated_data['organization'] = None
        
        try:
            with transaction.atomic():
                cls = Classroom.objects.create(**validated_data)
                Membership.objects.create(
                    user = request.user,
                    classroom = cls,
                    role = 'admin',
                    status = 'approved'
                )
        except Exception as e:
            raise serializers.ValidationError({'error': str(e)})
        
        return cls

        