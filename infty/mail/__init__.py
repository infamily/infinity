import logging

from django.core.mail import EmailMultiAlternatives
from celery import shared_task


logger = logging.getLogger(__name__)


@shared_task
def send_mail_task(subject, body, formatted_email_from, to, reply_to):

    msg = EmailMultiAlternatives(
        subject,
        body,
        formatted_email_from,
        to,
        reply_to=reply_to
    )

    msg.attach_alternative(body, "text/html")

    msg.send()


def send_mail_async(*args):
    return send_mail_task.apply_async(args)
