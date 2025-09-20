from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()



class Notice(models.Model):
    title = models.TextField()
    description = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_notices')
    organization = models.ForeignKey('organizations.Organization', on_delete=models.CASCADE, blank=True, null=True, related_name='notices')
    clasroom = models.ForeignKey('classrooms.Classroom', on_delete=models.CASCADE, blank=True, null=True, related_name='notices')
    classes = models.ForeignKey('classes.Class', on_delete=models.CASCADE, blank=True, null=True, related_name='notices')
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.title

class Assignment(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    classroom = models.ForeignKey('classrooms.Classroom', on_delete=models.CASCADE, related_name='assignments')
    class_obj = models.ForeignKey('classes.Class', on_delete=models.CASCADE, related_name='assignments')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_assignments")
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(null=True, blank=True)
    def __str__(self):
        return self.title
    
class AssignmentSubmission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assignments')
    classroom = models.ForeignKey("classrooms.Classroom", on_delete=models.CASCADE)
    class_obj = models.ForeignKey("classes.Class", on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)


class Organization(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255, null=True, blank=True)
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
    can_add_assignments = models.BooleanField(default=False)
    can_post_notices = models.BooleanField(default=False)
    can_add_members = models.BooleanField(default=False)
    status = models.CharField(choices=STATUS_CHOICES, default='pending', max_length=20)
    joined_at = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return f"{self.user.username} - {self.role} in {self.classroom or 'No Classroom'}"

    class Meta:
        indexes = [
            models.Index(fields=['classroom', 'role']),  
        ]
        ordering = ['-joined_at']  
        unique_together = ('user', 'classroom')  

    @property
    def is_admin(self):
        return self.role == 'admin'

    def save(self, *args, **kwargs):
        if not self.pk:
            if self.role in ['admin', 'moderator']:
                self.can_add_assignments = True
                self.can_post_notices = True
                self.can_add_members = True
            
        super().save(*args, **kwargs)







