import os
from typing import Dict, Any

import mailtrap as mt
from celery import shared_task
import environ

env = environ.Env()
environ.Env.read_env(os.path.join(os.path.dirname(__file__), '..', '.env'))


@shared_task(name='email_app.tasks.send_email_task')
def send_email_task(payload: Dict[str, Any]) -> None:
    """
    A Celery task that sends an email using the Mailtrap client.
    The 'payload' dictionary should contain keys 'automobile' and 'part'
    with relevant information about the uploaded file and the associated automobile.

    :param payload: A dictionary containing Automobile and Part information.
    :return: None
    """
    to_email = env('TO_EMAIL')
    automobile = payload.get('automobile', {})
    part = payload.get('part', {})

    subject = f"New File Uploaded for {automobile.get('manufacturer')} {automobile.get('model')}"
    message = f"""
            Hello,
            
            A new file was uploaded for the following automobile:
            
            Manufacturer: {automobile.get('manufacturer')}
            Model: {automobile.get('model')}
            Type: {automobile.get('type')}
            
            Part: {part.get('name')}
            File Link: {part.get('file_link')}
            
            Regards,
            Email Service
            """.strip()

    mail = mt.Mail(
        sender=mt.Address(email=env("FROM_EMAIL"), name="Automobile Management System"),
        to=[mt.Address(email=to_email)],
        subject=subject,
        text=message,
        category="Integration Test"
    )

    token = os.environ.get("MAILTRAP_TOKEN", env("MAILTRAP_TOKEN"))

    client = mt.MailtrapClient(token=token)
    response = client.send(mail)
