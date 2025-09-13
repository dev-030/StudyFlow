from django.db.models.signals import post_save
from django.dispatch import receiver
from organizations.models import Assignment, Membership, AssignmentSubmission


@receiver(post_save, sender=Assignment)
def create_entry_in_assignmentsubmission(sender, instance, created, **kwargs):
    if created:
        # # Find all students in the classroom of this assignment
        # students = Membership.objects.filter(
        #     classroom=instance.classroom,
        #     role='student'
        # )
        # # Create a submission entry for each student
        # submissions = [
        #     AssignmentSubmission(assignment=instance, student=s.user)
        #     for s in students
        # ]
        # AssignmentSubmission.objects.bulk_create(submissions)