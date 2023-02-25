from django.core.mail import send_mail
from django.conf import settings
from django.template import Context, loader
import requests
import os
from django.core.mail import EmailMessage

from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives


def send_verify_code(context):
    template = loader.get_template('otp.html')
    message = template.render(context)
    return requests.post(
        "https://api.mailgun.net/v3/checkcheckgoose.com/messages",
        auth=("api", "e23cf488db74bfc79adbe21f1d1d9e8c-52d193a0-70bd595a"),
        data={"from": "Checkcheckgoose <mailgun@checkcheckgoose.com>",
              "to": [context['user']],
              "subject": "Verify",
              "html": message})

def send_invite_member(context):
    template = loader.get_template('invitation.html')
    message = template.render(context)
    return requests.post(
        "https://api.mailgun.net/v3/checkcheckgoose.com/messages",
        auth=("api", "e23cf488db74bfc79adbe21f1d1d9e8c-52d193a0-70bd595a"),
        data={"from": "Checkcheckgoose <mailgun@checkcheckgoose.com>",
              "to": [context["user"]],
              "subject": "Invitation",
              "html": message})

def send_approval_notification(data):
    html_content = render_to_string("welcome.html", data)
    text_content = strip_tags(html_content)
    email = EmailMultiAlternatives(
        "Welcome",
        text_content,
        settings.EMAIL_HOST_USER ,
        ['dev1110upwork@gmail.com']
    )
    email.attach_alternative(html_content, 'text/html')
    email.send()


def send_approval_notification_mailgun(context):
    template = loader.get_template('welcome.html')
    message = template.render(context)
    return requests.post(
        "https://api.mailgun.net/v3/checkcheckgoose.com/messages",
        auth=("api", "e23cf488db74bfc79adbe21f1d1d9e8c-52d193a0-70bd595a"),
        data={"from": "Checkcheckgoose <mailgun@checkcheckgoose.com>",
              "to": ['dev1110upwork@gmail.com'],
              "subject": "Welcome!",
              "html": message})