from django.contrib.auth import get_user_model, login, logout, authenticate
from rest_framework.authentication import SessionAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import permissions, status
from .serializers import TokenSerializer
from .serializers import UserRegisterSerializer, UserLoginSerializer, UserSerializer
from .validations import custom_validation, validate_email, validate_password
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import render
from django.http import JsonResponse
from .models import AppUser
from .serializers import VerifyTokenSerializer

from django.shortcuts import redirect
from django.urls import reverse
#from google_auth_oauthlib.flow import Flow
#from google.oauth2.credentials import Credentials
#from googleapiclient.discovery import build
from django.conf import settings



class SendEmailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user

        if not user.google_credentials:
            return Response({"error": "Google credentials not found"}, status=status.HTTP_400_BAD_REQUEST)

        credentials = Credentials(**user.google_credentials)
        service = build('gmail', 'v1', credentials=credentials)

        email_data = request.data
        message = create_message(email_data['subject'], email_data['body'], email_data['to_email'])

        try:
            send_message(service, 'me', message)
            return Response({"success": "Email sent successfully"})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def create_message(subject, body, to_email):
    from email.mime.text import MIMEText
    import base64

    message = MIMEText(body)
    message['to'] = to_email
    message['subject'] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {'raw': raw}

def send_message(service, user_id, message):
    service.users().messages().send(userId=user_id, body=message).execute()

class VerifyTokenView(APIView):
  permission_classes = [IsAuthenticated]  # Only authenticated users can access

  def post(self, request):
    serializer = VerifyTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    return Response({'valid': True})  # Return success response if token is valid





class UserInformationView(APIView):
  permission_classes = [IsAuthenticated]  # Only authenticated users can access

  def get(self, request):
    """Retrieves and returns the currently authenticated user's information."""
    user = request.user  # Access the authenticated user

    # You can customize the data returned based on your needs
    user_data = {
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
    }
    return Response(user_data)




class UserRegister(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        clean_data = custom_validation(request.data)
        serializer = UserRegisterSerializer(data=clean_data)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLogin(APIView):
    serializer_class = UserLoginSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']

            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                return Response(status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

class UserLogout(APIView):
    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(status=205)  # No content response

class ObtainTokenPairView(TokenObtainPairSerializer):
    # ... your custom token view logic (optional)
    pass

class UserView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (SessionAuthentication,)

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response({'user': serializer.data}, status=status.HTTP_200_OK)
    
class HomeView(APIView):
   permission_classes = (permissions.IsAuthenticated, )
   def get(self, request):
       content = {'message': "Welcome to the JWT  Authentication page using React Js and Django!"}
       return Response(content)
   
class LogoutView(APIView):
     permission_classes = (IsAuthenticated,)
     def post(self, request):
          
          try:
               refresh_token = request.data["refresh_token"]
               token = RefreshToken(refresh_token)
               token.blacklist()
               return Response(status=status.HTTP_205_RESET_CONTENT)
          except Exception as e:
               return Response(status=status.HTTP_400_BAD_REQUEST)