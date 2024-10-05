from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model


def custom_validation(data):
  email = data['email'].strip()
  password = data['password'].strip()

  # Check if email is empty or already exists in the database
  UserModel = get_user_model()
  if not email or UserModel.objects.filter(email=email).exists():
    raise ValidationError('Choose another email')
  
  # Check if password is empty or less than 8 characters
  if not password or len(password) < 8:
    raise ValidationError('Choose another password, minimum 8 characters')

  return data


def validate_email(data):
    email = data['email'].strip()

    # Check if email is empty
    if not email:
        raise ValidationError('An email is needed')

    return True



def validate_password(data):
    password = data['password'].strip()

    # Check if password is empty
    if not password:
        raise ValidationError('A password is needed')

    return True