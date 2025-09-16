from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Membership
from .serializers import MembershipSerializer, OrganizationSerializer
from rest_framework.generics import CreateAPIView



class Memberships(APIView):
    def get(self, request):
        memberships = Membership.objects.filter(user=request.user).select_related('organization', 'classroom', 'classes')
        serializer = MembershipSerializer(memberships)
        return Response(serializer.data, status=status.HTTP_200_OK)
    


class OrganizationView(CreateAPIView):
    serializer_class = OrganizationSerializer
