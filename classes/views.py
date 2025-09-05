from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Class
from django.db import transaction
import re
from organizations.models import Membership


class ClassView(APIView):
    def post(self, request):
        name = request.data.get('name').strip()
        if not name:
            return Response({"error": "A name is required"}, status=status.HTTP_400_BAD_REQUEST)
        if len(name) > 100:
            return Response({"error": "Name too long"}, status=status.HTTP_400_BAD_REQUEST)
        if not re.fullmatch(r"[A-Za-z0-9\s\-]+", name):
            return Response({"error":"Invalid characters in name"}, status=status.HTTP_400_BAD_REQUEST)
        
        
        try:
            with transaction.atomic():
                cls = Class.objects.create(
                    name = name,
                    admin = request.user
                )

                Membership.objects.create(
                    user = request.user,
                    classes = cls,
                    role = 'admin',
                    status = 'approved'
                )

                return Response({
                    "id": cls.id,
                    "name": cls.name,
                    "admin": cls.admin.id,
                    "classroom": cls.classroom,
                    "created_at": cls.created_at
                }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

