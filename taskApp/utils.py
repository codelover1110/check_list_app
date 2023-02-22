from django.core.mail import send_mail
from django.conf import settings
from django.template import Context, loader
import requests
import os
from django.core.mail import EmailMessage

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
    subject = f"Hi, You were added as a team member of Workspace - {data['workspace_name']}"
    message = f"http://34.67.86.53:8000/ \n\nChecklist Website: Please signin."
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [user_email,]
    print (' +++++ verification code for {}: {}'.format(user_email, data))
    send_mail(subject, message, email_from, recipient_list )

def send_approval_notification(data, user_email):
    subject = f"Hi, Admin. It is for approval from {data['submit_user']}"
    message = f"Workspace: {data['workspace_name']}, List: {data['list_name']} https://checkcheckgoose.com/workspace/{data['workspace_id']}/list/{data['list_id']}/approve-tasks \n\nChecklist"
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [user_email,]
    print (' +++++ verification code for {}: {}'.format(user_email, data))
    send_mail(subject, message, email_from, recipient_list )

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


