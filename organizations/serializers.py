from rest_framework import serializers
from .models import Membership, Organization
import re
from django.db import transaction






class MembershipSerializer(serializers.Serializer):

    organizations = serializers.ListField(child=serializers.DictField(), read_only=True)
    classrooms = serializers.ListField(child=serializers.DictField(), read_only=True)
    classes = serializers.ListField(child=serializers.DictField(), read_only=True)

    def to_representation(self, instance):
        response = {"organization":[], "classroom":[], "classes":[]}

        for membership in instance:
            if membership.organization:
                response["organization"].append({
                    "id": membership.organization.id,
                    "name": membership.organization.name,
                    "role": membership.role
                })
            elif membership.classroom:
                response['classroom'].append({
                    "id": membership.classroom.id,
                    "name": membership.classroom.name,
                    "role": membership.role
                })
            elif membership.classes:
                response['classes'].append({
                    "id": membership.classes.id,
                    "name": membership.classes.name,
                    "role": membership.role
                })

        return response




class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ["id", "name", "created_by", "created_at"]
        read_only_fields = ["id", "created_by", "created_at"]

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
        validated_data['created_by'] = request.user

        try:
            with transaction.atomic():
                org = Organization.objects.create(**validated_data)
                Membership.objects.create(
                    user=request.user,
                    organization = org,
                    role = "admin",
                    status = "approved"
                )
        except Exception as e:
            raise serializers.ValidationError({'error': str(e)})  
        
        return org      

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        action = getattr(self.context.get('view'), 'action', None) 
        if action in ['create', 'update']:
            self.fields['name'].required = True
        else:
            self.fields['name'].required = False