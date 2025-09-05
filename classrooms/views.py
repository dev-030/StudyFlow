from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import re
from django.db import transaction
from .models import Classroom
from organizations.models import Membership


class ClassroomView(APIView):
    permission_classes = [IsAuthenticated]
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
                classroom = Classroom.objects.create(
                    name = name,
                    admin = request.user
                )
                Membership.objects.create(
                    user = request.user,
                    role = 'admin',
                    status = 'approved',
                    classroom = classroom
                )

                return Response({
                    "id": classroom.id,
                    "name": classroom.name,
                    "organization": classroom.organization,
                    "admin": classroom.admin.id,
                    "created_at": classroom.created_at
                }, status=status.HTTP_201_CREATED)

        except Exception as e :
            return Response({"error" : str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            


