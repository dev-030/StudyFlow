from django.urls import path, include
from .views import Memberships, OrganizationView
from rest_framework.routers import DefaultRouter
from .views import OrganizationViewSet


router = DefaultRouter()
router.register(r'organization', OrganizationViewSet, basename='organization')


urlpatterns = [
  path('memberships/', Memberships.as_view(), name='user_register'),
  path('', include(router.urls))
  # path('', OrganizationView.as_view(), name='create-organization'),
]

