from django.db.models.signals import post_save
from django.dispatch import receiver
from organizations.models import Assignment, Membership, AssignmentSubmission


@receiver(post_save, sender=Assignment)
def create_entry_in_assignmentsubmission(sender, instance, created, **kwargs):
    if created:
        students = Membership.objects.filter(
            classroom = instance.classroom,
            role = 'student'
        ).values_list('user', flat=True)

        submissions = [
            AssignmentSubmission(
                assignment = instance,
                student_id = student_id,
                classroom = instance.classroom,
                class_obj = instance.class_obj
            )
            for student_id in students
        ]

        AssignmentSubmission.objects.bulk_create(submissions)
