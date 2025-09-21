from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Class
from django.db import transaction
import re
from organizations.models import Membership
from classrooms.models import Classroom
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from rest_framework import viewsets
from .serializers import ClassSerializer



User = get_user_model()



class ClassViewSet(viewsets.ModelViewSet):
    queryset = Class.objects.all()
    serializer_class = ClassSerializer

    


# class ClassView(APIView):
#     def post(self, request):
#         name = request.data.get('name').strip()
#         classroom_id = request.data.get('id')
#         if not name:
#             return Response({"error": "A name is required"}, status=status.HTTP_400_BAD_REQUEST)
#         if len(name) > 100:
#             return Response({"error": "Name too long"}, status=status.HTTP_400_BAD_REQUEST)
#         if not re.fullmatch(r"[A-Za-z0-9\s\-]+", name):
#             return Response({"error":"Invalid characters in name"}, status=status.HTTP_400_BAD_REQUEST)
        
#         try:
#             with transaction.atomic():
#                 classroom = None
#                 if classroom_id:
#                     try:
#                         classroom = Classroom.objects.filter(id=classroom_id).first()
#                         if classroom.admin != request.user:
#                             classroom = None
#                     except classroom.DoesNotExist:
#                         classroom = None
                
#                 cls = Class.objects.create(
#                     name = name,
#                     admin = request.user,
#                     classroom = classroom
#                 )

#                 Membership.objects.create(
#                     user = request.user,
#                     classes = cls,
#                     role = 'admin',
#                     status = 'approved'
#                 )

#                 return Response({
#                     "id": cls.id,
#                     "name": cls.name,
#                     "admin": cls.admin.id,
#                     "classroom": cls.classroom.name if classroom else None,
#                     "created_at": cls.created_at
#                 }, status=status.HTTP_201_CREATED)

#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        



class AddStudentsView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        email = request.data.get('email')
        class_id = request.data.get('class_id')
        if not email or not class_id:
            return Response({"error": "both class_id and email are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        membership= Membership.objects.filter(
            classes = class_id,
            user = request.user,
            role = 'admin'
        ).first()

        if not membership:
            return Response(
            {"error": "Class not found or you are not admin"},
            status=status.HTTP_403_FORBIDDEN
        )

        try:      
            user = User.objects.get(email=email)
        except Membership.DoesNotExist:
            return Response({"error":"user with this email does not exists"}, status=status.HTTP_400_BAD_REQUEST)
        
        if membership.objects.filter(classes = class_id, user=user, role='student').exists():
            return Response({"error": "User is already a member of this class"}, status=status.HTTP_400_BAD_REQUEST)
        
        Membership.objects.create(
            user = user,
            classes= class_id,
            role = 'student',
            status = 'approved'
        )

        return Response({"success": "Student added successfully"}, status=status.HTTP_201_CREATED)

        

