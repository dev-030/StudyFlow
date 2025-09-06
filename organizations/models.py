from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Organization(models.Model):
    name = models.CharField(max_length=255)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_organizations")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name



class Membership(models.Model):
    ROLES = [
        ('admin', 'Admin'),
        ('moderator', 'Moderator'),
        ('cr', 'Class Representative'),
        ('student', 'Student')
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='memberships')
    organization = models.ForeignKey(Organization, null=True, blank=True, on_delete=models.CASCADE)
    classroom = models.ForeignKey('classrooms.Classroom', blank=True, null=True, on_delete=models.CASCADE, related_name='memberships')
    classes = models.ForeignKey('classes.Class', null=True, blank=True, on_delete=models.CASCADE)
    role = models.CharField(choices=ROLES, max_length=20)
    status = models.CharField(choices=STATUS_CHOICES, default='pending', max_length=20)
    joined_at = models.DateTimeField(auto_now_add=True)






