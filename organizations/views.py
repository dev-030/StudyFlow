from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Membership, Organization
from .serializers import MembershipSerializer
import re
from django.db import transaction




class Memberships(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        memberships = Membership.objects.filter(user=request.user)
        serializer = MembershipSerializer(memberships, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class OrganizationView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):

        name = request.data.get('name', "").strip()

        if not name:
            return Response({"error":"name is required"}, status=status.HTTP_400_BAD_REQUEST)
        if len(name) > 100:
            return Response({"error": "Name too long"}, status=status.HTTP_400_BAD_REQUEST)
        if not re.fullmatch(r"[A-Za-z0-9\s\-]+", name):
            return Response({"error":"Invalid characters in name"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            with transaction.atomic():
                org = Organization.objects.create(name=name, created_by=request.user)
                Membership.objects.create(user=request.user, organization = org, role = 'admin', status = 'approved')
        except InterruptedError:
            return Response({'error': 'Internal server error'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "id": org.id,
            "name": org.name,
            "created_by": org.created_by.id,
            "created_at": org.created_at
        }, status=status.HTTP_201_CREATED)