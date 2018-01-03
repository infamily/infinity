import logging

from celery import shared_task

from django.core.mail import (
    EmailMultiAlternatives,
    get_connection,
)


logger = logging.getLogger(__name__)


@shared_task
def send_mail_task(subject, body, formatted_email_from, to, reply_to,
                   email_backend):

    connection = get_connection(email_backend)

    msg = EmailMultiAlternatives(
        subject,
        body,
        formatted_email_from,
        to,
        reply_to=reply_to,
        connection=connection)

    msg.attach_alternative(body, "text/html")

    msg.send()


def send_mail_async(*args):
    return send_mail_task.apply_async(args, countdown=2)
