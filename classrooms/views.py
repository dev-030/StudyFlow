from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import re
from django.db import transaction
from .models import Classroom
from organizations.models import Membership, Organization
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from classes.models import Class
from django.db.models import F
from rest_framework import viewsets, exceptions
from .serializers import ClassroomSerializer




User = get_user_model()


class ClassroomView(APIView):

    def get(self, request):
        clsroom_id = request.data.get('classroom_id')

        if not clsroom_id:
            return Response({"error": "classroom_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        classes = list(Class.objects.filter(
            classroom_id = clsroom_id,
            classroom__memberships__user = request.user,
            classroom__memberships__status = 'approved'
        ).annotate(role = F('classroom__memberships__role'))
        .values("id", "name", "role"))

        if not classes:
            return Response({"error": "Either classroom not found or you don’t have access"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"data": classes}, status=status.HTTP_200_OK)


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
                    "organization": classroom.organization.name if organization else None,
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


# class ClassroomViewSet(viewsets.ModelViewSet):
#     serializer_class = ClassroomSerializer
#     queryset = Classroom.objects.all()

#     def update(self, request, *args, **kwargs):
#         if not request.user.is_staff:
#             raise exceptions.PermissionDenied("User must be an admin to update classroom name.")
#         return super().update(request, *args, **kwargs)
    



class AddStudentsView(APIView):
    def post(self, request):
        clsroom_id = request.data.get('classroom_id')
        email = request.data.get('email')
        if not clsroom_id or not email:
            return Response({"error":"both email and classroom_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        classroom = get_object_or_404(Classroom, id=clsroom_id)

        is_admin = Membership.objects.filter(user=request.user, classroom=classroom, role="admin").exists()

        if not is_admin:
            return Response({"error":"class does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist: 
            return Response({"error":"user does not exist"}, status=status.HTTP_404_NOT_FOUND)
        
        membership, created = Membership.objects.get_or_create(
            user = user,
            classroom = clsroom_id,
            role = 'student',
            status = 'approved'
        )

        if not created:
            return Response({"error": "User already exists in this classroom"},status=status.HTTP_400_BAD_REQUEST)

        return Response({"message":"user successfully added to the classroom "}, status=status.HTTP_201_CREATED)
        
