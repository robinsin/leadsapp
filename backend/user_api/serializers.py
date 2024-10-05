from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from .models import AppUser

def validate_email(email):
  # Implement your custom email validation logic here
  # This example checks for a basic email format
  if not '@' in email or not '.' in email:
    raise ValidationError('Invalid email format')
  return email

def validate_password(password):
  # Implement your custom password validation logic here
  # This example checks for minimum password length
  if len(password) < 8:
    raise ValidationError('Password must be at least 8 characters long')
  return password

class UserSerializer(serializers.ModelSerializer):
  class Meta:
    model = AppUser
    fields = ('email', 'first_name', 'last_name')
    
class TokenSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        refresh = attrs['refresh']
        try:
            token = RefreshToken(refresh)
            token.blacklist()
        except Exception as e:
            raise serializers.ValidationError(f'Token is invalid or expired: {e}')
        return attrs	

class UserRegisterSerializer(serializers.ModelSerializer):
  class Meta:
        model = AppUser
        fields = ['email', 'first_name', 'last_name', 'password']
        extra_kwargs = {'password': {'write_only': True}}

  def create(self, validated_data):
        password = validated_data.pop('password')
        user = AppUser(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserLoginSerializer(serializers.Serializer):
  email = serializers.EmailField()
  password = serializers.CharField()

    # ... other serializers ...
  def validate(self, attrs):
    email = attrs.get('email')
    password = attrs.get('password')

    # Perform custom validation on email and password
    validate_email(email)
    validate_password(password)

    # Use Django's authentication to check credentials
    user = authenticate(email=email, password=password)
    if not user:
      raise serializers.ValidationError('Invalid email or password')
    attrs['user'] = user
    return attrs
  
  
class VerifyTokenSerializer(serializers.Serializer):
  token = serializers.CharField()

  def validate(self, attrs):
    token = attrs.get('token')
    refresh = RefreshToken(token)
    try:
      refresh.check_isActive()  # Check if token is active (not expired)
      return attrs
    except Exception as e:
      raise serializers.ValidationError('Invalid or expired token')