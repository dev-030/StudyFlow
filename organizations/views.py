from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Membership
from .serializers import MembershipSerializer, OrganizationSerializer
from rest_framework.generics import CreateAPIView
from rest_framework import viewsets
from classrooms.models import Classroom
from rest_framework.exceptions import PermissionDenied
from .models import Organization



class Memberships(APIView):
    def get(self, request):
        memberships = Membership.objects.filter(user=request.user).select_related('organization', 'classroom', 'classes')
        serializer = MembershipSerializer(memberships)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class OrganizationView(CreateAPIView):
    serializer_class = OrganizationSerializer

    

class OrganizationViewSet(viewsets.ModelViewSet):
    
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer

    def list(self, request, *args, **kwargs):
        org_id = request.query_params.get('org_id')
        if not org_id:
            return Response({"error": "Organization id is required"})
        
        classrooms = Classroom.objects.filter(
            organization_id=org_id, 
            organization__membership_set__user=request.user, 
            organization__membership_set__status='approved'
        ).values('id', 'name').distinct()

        return Response(list(classrooms), status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied("Only admins can update organization name")
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied("Only admins can delete organization")
        return super().destroy(request, *args, **kwargs)
    
    