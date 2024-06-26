import os

from celery import shared_task
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from PIL import Image

from .core_utils.token import account_activation_token


def send_activation_email(current_site, user):
    subject = 'Activate Your Ecommerce App Account'
    message = render_to_string('core/account_activation_email.html',
    {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
    })
    send_activate_email.delay(subject, message, user.email)

@shared_task(name="activation email")
def send_activate_email(subject, message, email):
    #user.email_user(subject, message)
    send_mail(subject=subject, message=message, from_email="donotreply@ecom.com", recipient_list=[email])


@shared_task(name="update email")
def send_update_notification(username, email):
    subject = 'Profile Update Successful'
    message = f'''
Hello {username},
Your Account Profile Has been updated.

If you did not initiate this request, change your password immediately. 
Also email support to inform us about it.
'''
    send_mail(subject=subject, message=message,from_email="donotreply@ecom.com", recipient_list=[email])


#will add celery shared task decorator later
@shared_task(name="process user image")
def process_user_image(imagepath)->None:
    #this operation adds computational overhead each time a save/update to models is done
    #needs to be reviewed -> Done
    print("processing image")#will replace all prints with logging properly
    img = Image.open(imagepath)

    if img.height > 150 or img.width > 150:
        output_size = (150, 150)  # 125,125 was used in flask example though
        img.thumbnail(output_size)
        img.save(imagepath)

@shared_task(name="delete previous image")
def del_prev_image(imagepath):
    #remove old file
    print("deleting image")
    try:
        os.remove(imagepath)
        return "Success"#will remove later
    except FileNotFoundError:
        print("file not found")#will replace with log
