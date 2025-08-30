from celery import shared_task
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from celery.exceptions import Ignore



User = get_user_model()



@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def send_verification_email(self, user_id, uid, token):
    try:
        user = User.objects.get(pk=user_id)
        verification_url =  f"http://localhost:8000/auth/verify-email/{uid}/{token}/"
        print('Sending verification mail....🟢')
        send_mail(
            subject="Verify your studyflow account",
            message=f"click the link to verify your account: {verification_url}",
            from_email="onboarding@resend.dev",
            recipient_list=[user.email],
            fail_silently=False
        )
    except Exception as exc:
        if self.request.retries >= self.max_retries:
            User.objects.get(pk=user_id).delete()
            print('Failed to send mail....🔴')
            raise Ignore()
        else:
            raise self.retry(exc=exc, countdown=10)