import os
from typing import cast, Dict
import copy

from django.core.mail import send_mail


"""email = EmailMessage(
subject="Hello",
body="Body goes here",
from_email="from@example.com",
to=["to1@example.com"],
bcc=["bcc@example.com"],
headers={"Custom-Header": "Value"},
)
email.attach("file.txt", "File content", "text/plain")
email.send()"""

EMAIL_TOPICS: Dict[str, Dict[str, str]] = {
    'new_password':{
        'subject': 'making new password',
        'message' : f'Verify yourself by using this verification code to make your new password. your verification code is\n'
        }
}

def prepare_dynamic_email_contents(topic:str, **kwargs):
    email_contents = copy.deepcopy(EMAIL_TOPICS.get(topic))
    if email_contents is None:
        raise ValueError('no content topic')

    if topic == 'new_password':
        email_contents['message'] = cast(str, email_contents.get('message')) + str(kwargs.get('v_code'))

    return email_contents

def send_email(topic: str, email: str, **kwargs):

    email_contents = prepare_dynamic_email_contents(topic= topic, **kwargs)

    if email_contents is None:
        raise ValueError("No email content found for specified topic")
    
    send_mail(
        subject = cast(str, email_contents.get('subject')),
        message = cast(str, email_contents.get('message')),
        from_email= os.getenv('USER_EMAIL'),
        recipient_list=[email],
        fail_silently=False,
    )
