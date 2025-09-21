from django.urls import path, include
# from .views import ClassroomView
from rest_framework.routers import DefaultRouter
from .views import ClassroomViewset



router = DefaultRouter()
router.register(r'', ClassroomViewset, basename='classrooms')


urlpatterns = [
  # path('', ClassroomView.as_view(), name='create_classroom'),
  path('', include(router.urls))
]