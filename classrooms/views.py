from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import re
from django.db import transaction
from .models import Classroom
from organizations.models import Membership, Organization


class ClassroomView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        name = request.data.get('name', '').strip()
        org = request.data.get('org_id')
        if not name:
            return Response({"error": "A name is required"}, status=status.HTTP_400_BAD_REQUEST)
        if len(name) > 100:
            return Response({"error": "Name too long"}, status=status.HTTP_400_BAD_REQUEST)
        if not re.fullmatch(r"[A-Za-z0-9\s\-]+", name):
            return Response({"error":"Invalid characters in name"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            with transaction.atomic():
                organization = None

                if org:
                    try:
                        organization = Organization.objects.get(id=org)
                        if organization.created_by != request.user:
                            organization = None
                    except organization.DoesNotExist:
                        organization = None

                print(organization, organization.id, '🔴')

                classroom = Classroom.objects.create(
                    name = name,
                    admin = request.user,
                    organization = organization
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
                    "organization": classroom.organization.name,
                    "admin": classroom.admin.id,
                    "created_at": classroom.created_at
                }, status=status.HTTP_201_CREATED)

        except Exception as e :
            return Response({"error" : str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    
    def patch(self, request):
        name  = request.data.get('name')
        id = request.data.get('id')
        try:
            membership = Membership.objects.filter(
                user = request.user,
                classroom_id = id
            ).first()
            if membership and membership.role == 'admin':
                Classroom.objects.filter(id=id).update(name=name)
                return Response({"message": "classroom name updated successfully..."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response ({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        
    def delete(self,request):
        id = request.data.get('id')
        try:
            membership = Membership.objects.filter(
                user = request.user,
                classroom_id = id
            ).first()
            if membership and membership.role == 'admin':
                Classroom.objects.filter(id=id).delete()
                return Response({"message": "Classroom deleted successfully"})
        except Exception as e :
            return Response({"errror": str(e)}, status=status.HTTP_400_BAD_REQUEST)


