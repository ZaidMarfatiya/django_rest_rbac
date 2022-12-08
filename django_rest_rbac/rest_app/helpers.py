from django.contrib.auth.tokens import default_token_generator, PasswordResetTokenGenerator
from rest_app.utils import send_email

def verify_email(request, user, uid):
    email_token = default_token_generator.make_token(user)

    data = {
        'subject': 'Verify Your Email',
        'body': f"Please click on this {request.scheme}://{request.get_host()}/verify-email/{uid}/{email_token} link for verify email",
        'to_email': user.email
    }
    send_email(data)


def forgot_password_email(request, user, uid):
    token = PasswordResetTokenGenerator().make_token(user)

    data = {
        'subject': 'Reset Your Password',
        'body': f"Please click on this {request.scheme}://{request.get_host()}/forgot-password/{uid}/{token} for resest password",
        'to_email': user.email
    }
    send_email(data)