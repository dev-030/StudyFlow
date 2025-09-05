from django.urls import path
from .views import Memberships, OrganizationView


urlpatterns = [
  path('memberships/', Memberships.as_view(), name='user_register'),
  path('', OrganizationView.as_view(), name='create-organization')
]