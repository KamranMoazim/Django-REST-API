from time import sleep
# from storefront.celery import celery   # dependent approach
from celery import shared_task    # better approach

# @celery.task
@shared_task
def notify_customers(message):
    print("sending 10K emails....")
    print(message)
    sleep(10)
    print("Emails sent successfully!")