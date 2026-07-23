from time import sleep
from typing import cast, Any

from celery import shared_task, Task
from celery.signals import task_success, task_failure
from django.core.mail import send_mail
from django_celery_beat.models import PeriodicTask, IntervalSchedule, CrontabSchedule

#from base import services as core_services
from .services import OrderCreationService

#run task with
# celery -A VeggieVault worker -l info --pool=gevent
# celery -A proj beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler    

@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={"max_retries": 3})
def expire_stale_orders_task(self, *args, **kwargs):
    """Celery task to call expire_stale_orders_task service."""
    try:
        print("Entering in expire_stale_orders_task")
        print("kwargs:",kwargs)
        order_id = kwargs.get('order_id')
        if not order_id:
            raise Exception("need order id to proceed")
        
        OrderCreationService.expire_stale_orders(order_id = order_id)
        
        print("leaving expire_stale_orders_task")
        return f"done"
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)



@shared_task
def say_hello_task():
    print("hello")

    
@task_success.connect
def on_success(sender=None, result=None, **kwargs):
   sender = cast(Task, sender)
   print(f"Task {sender.name} succeeded with result: {result}")

@task_failure.connect
def on_failure(sender=None, exception=None, traceback=None, **kwargs):
   sender = cast(Task, sender)
   print(f"Task {sender.name} failed with exception: {exception}")