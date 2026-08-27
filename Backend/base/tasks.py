import logging
from time import sleep, time
from typing import cast, Any

from celery import shared_task, Task
from celery.signals import task_success, task_failure
from django.core.mail import send_mail
#from django_celery_beat.models import PeriodicTask, IntervalSchedule, CrontabSchedule

from base import services as core_services



#run task with
#celery -A VeggieVault worker -l info --pool=solo
# celery -A VeggieVault worker -l info --pool=gevent
#celery -A VeggieVault beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler

@shared_task(bind=True, retry_kwargs={"max_retries": 3})
def send_email_task(self:Task, topic: str, email: str, v_code: str):
    """Sends an email when the feedback form has been submitted."""
    try:
        core_services.send_email(topic= topic, email=email, v_code=v_code)
        return f"Email sent successfully to {email}"
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)
    

@shared_task #repeating task
def say_hello_task():
    print(f"Celery interval task is running, its [{time.strftime('%H:%M:%S')}]: Hello from Celery!!!")

    
@task_success.connect
def on_success(sender=None, result=None, **kwargs):
   sender = cast(Task, sender)
   print(f"Task {sender.name} succeeded with result: {result}")

@task_failure.connect
def on_failure(sender=None, exception=None, traceback=None, **kwargs):
   sender = cast(Task, sender)
   print(f"Task {sender.name} failed with exception: {exception}")


