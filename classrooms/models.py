from django.db import models
from django.contrib.auth import get_user_model



User = get_user_model()


class Classroom(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=255, null=True, blank=True, default="")
    admin = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name='created_classrooms')
    organization = models.ForeignKey('organizations.Organization', blank=True, null=True, on_delete=models.CASCADE, related_name='classrooms')
    created_at = models.DateTimeField(auto_now_add=True)
