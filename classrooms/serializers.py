from rest_framework import serializers
from .models import Classroom
import re





class ClassroomSerializer(serializers.ModelSerializer):

    class Meta:
        models = Classroom
        fields = ["id, name"]

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Name is required")
        if len(value) > 100:
            raise serializers.ValidationError("Name too long")
        if not re.fullmatch(r"[A-Za-z0-9\s\-]+", value):
            raise serializers.ValidationError("Invalid characters in name")
        return value

    # def create(self, validated_data):
        