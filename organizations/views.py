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
from django.db.models import Count, F




class Memberships(APIView):
    def get(self, request):
        print(request.user,'🔴')
        memberships = Membership.objects.filter(user=request.user).select_related(
            'organization',
            'classroom',
            'classes'
            ).annotate(
                classroom_count = Count('organization__classrooms', distinct=True),
                class_count = Count('classroom__classes', distinct=True),
                organization_members = Count('organization__membership', distinct=True),
                classroom_members = Count('classroom__memberships', distinct=True),
                class_members = Count('classes__membership', distinct=True)
            )
        serializer = MembershipSerializer(memberships)
        return Response(serializer.data, status=status.HTTP_200_OK)




class OrganizationViewSet(viewsets.ModelViewSet):
    
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer

    def list(self, request, *args, **kwargs):
        org = Organization.objects.filter(
            membership__user = request.user,
            membership__status = 'approved'
        ).annotate(
            classroom_count = Count('classrooms', distinct=True),
            member_count = Count('membership', distinct=True),
            role = F('membership__role')
        ).values('id', 'name', 'description', 'role', 'classroom_count', 'member_count')
        return Response(list(org), status=status.HTTP_200_OK)
    
    def retrieve(self, request, pk, *args, **kwargs):

        org = Organization.objects.filter(
            id = pk,
            membership__user = request.user,
            membership__status = 'approved'
        ).annotate(
            role = F('membership__role'),
            member_count = Count('membership')
        ).prefetch_related('classrooms')
        # .values('id', 'name', 'description', 'role', 'member_count', 'created_at')


        return Response(org, status=status.HTTP_200_OK)


    # def list(self, request, *args, **kwargs):

        # org_id = request.query_params.get('org_id')
        # if not org_id:
        #     return Response({"error": "Organization id is required"})
        
        # classrooms = Classroom.objects.filter(
        #     organization_id=org_id, 
        #     organization__membership_set__user=request.user, 
        #     organization__membership_set__status='approved'
        # ).values('id', 'name').distinct()

        # return Response(list(classrooms), status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied("Only admins can update organization name")
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied("Only admins can delete organization")
        return super().destroy(request, *args, **kwargs)
    
    