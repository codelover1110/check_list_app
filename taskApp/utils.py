from django.core.mail import send_mail
from django.conf import settings
from django.template import Context, loader
import requests
import os
from django.core.mail import EmailMessage

from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives

def send_phone(user_code, phone_number):
    account_sid = ''
    auth_token = ''

    client = None
    # client = Client(account_sid, auth_token)

    message = client.message_create(
        body = f'Hi, Your user and verification code is {user_code}',
        from_ = '',
        to = f'{phone_number}'
    )
    print(message.sid)

def send_email(user_code, user_email, stripe):
    subject = 'Hi, You would need to reset password for ThirtyTwo'
    message = user_code+" \n32andyou.io partners with Stripe for secure payments and financial services.\nConnect using this link "+stripe
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [user_email,]
    print (' +++++ verification code for {}: {}'.format(user_email, user_code))
    send_mail(subject, message, email_from, recipient_list )

def send_verify_code(user_code, user_email):
    subject = 'Hi, Please verify your device for Check List App'
    message = f"Verification code: {user_code}"
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [user_email,]
    print (' +++++ verification code for {}: {}'.format(user_email, user_code))
    send_mail(subject, message, email_from, recipient_list )

def send_invite_member(data, user_email):
    html_content = render_to_string("invitation.html", data)
    text_content = strip_tags(html_content)
    email = EmailMultiAlternatives(
        "Test HTML Email",
        text_content,
        settings.EMAIL_HOST_USER ,
        [user_email]
    )
    email.attach_alternative(html_content, 'text/html')
    email.send()


def send_email_teammember(data, user_email):
    subject = f"Hi, You were added as a team member of {data['office_name']}"
    message = f"http://34.67.86.53:8000/ \n\nOffice Website: {data['office_website']} \n\nStripe Url: {data['stripe_url']} \n\nPhone Number: {data['phone_number']}"
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [user_email,]
    print (' +++++ verification code for {}: {}'.format(user_email, data))
    send_mail(subject, message, email_from, recipient_list )

def send_welcome_email(payment_link, user_email):
    subject = f'Hi, {user_email}'
    message = f"payment link: {payment_link}"
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [user_email,]
    print (' +++++ verification code for {}: {}'.format(user_email, payment_link))
    send_mail(subject, message, email_from, recipient_list )
    # template = loader.get_template('welcome.html')
    # context = {"name": subscribe_data['customer_name'], "selected_team": subscribe_data['selected_team'], }
    # message = template.render(context)
    # mail = EmailMessage(
    #     subject="Wolvine.live Newsletter Subscription",
    #     body=message,
    #     from_email=settings.EMAIL_HOST_USER,
    #     to=[subscribe_data['email']],
    #     reply_to=[settings.EMAIL_HOST_USER],
    # )
    # mail.content_subtype = "html"
    # mail.send()

    # return requests.post(
    #     "https://api.mailgun.net/v3/tailgate.live/messages",
    #     auth=("api", "d32f998708037a38e350e7eba0d64cba-18e06deb-8000efa8"),
    #     data={"from": "Tailgate.Live <hey@tailgate.live>",
    #           "to": [subscribe_data['email']],
    #           "subject": "Welcome to Tailgate.live, thank you for subscribing!",
    #           "html": message})


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


