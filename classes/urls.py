from django.urls import path
from .views import ClassView


urlpatterns = [
  path('', ClassView.as_view(), name='create_class'),
]