import os
from typing import cast, Dict
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
def send_email(subject: str, email: str, **kwargs):
    emails_topics: dict[str, dict[str, str]] = {
        'new_password': {
            'subject': 'making new password',
            'message' : f'Verify yourself by using this verification code to make your new password. your verification code is\n{kwargs.get('v_code')}',
        } if 'v_code' in kwargs.keys() else {},
    }
    
    email_contents = cast(Dict[str, str], emails_topics.get(subject))
    if email_contents is None:
        raise ValueError("No email content found for specified subject")
    
    send_mail(
        subject = cast(str, email_contents.get('subject')),
        message = cast(str, email_contents.get('message')),
        from_email= os.getenv('USER_EMAIL'),
        recipient_list=[email],
        fail_silently=False,
    )