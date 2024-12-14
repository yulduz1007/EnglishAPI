from celery import shared_task
from django.core.mail import send_mail

from root import settings


@shared_task
def send_email(email, code):
    message = f"Code: {code}"
    send_mail("Code", message, settings.EMAIL_HOST_USER, [email])
    return {"message": f"Successfully sent email to {email}"}


