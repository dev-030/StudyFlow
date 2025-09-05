from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('authentication.urls'), name='authentication'),
    path('organizations/', include('organizations.urls'), name='organization'),
    path('classrooms/', include('classrooms.urls'), name='classrooms'),
    path('classes/', include('classes.urls'), name='classes')
]
