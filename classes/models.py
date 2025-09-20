from django.db import models
from django.contrib.auth import get_user_model



User = get_user_model()

class Class(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=255, null=True, blank=True)
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_classes')
    classroom = models.ForeignKey('classrooms.Classroom', blank=True, null=True, on_delete=models.CASCADE, related_name='classes')
    created_at = models.DateTimeField(auto_now_add=True)