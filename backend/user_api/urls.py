from django.urls import path
from . import views
from .views import VerifyTokenView
from .views import SendEmailView

urlpatterns = [
	path('register', views.UserRegister.as_view(), name='register'),
	path('login', views.UserLogin.as_view(), name='login'),
	#path('logout', views.UserLogout.as_view(), name='logout'),
    path('logout/', views.LogoutView.as_view(), name ='logout'),
    path('api/user2/', views.UserInformationView.as_view(), name='user_info'),
    path('verify/', VerifyTokenView.as_view()),

	path('user', views.UserView.as_view(), name='user'),
    path('home/', views.HomeView.as_view(), name ='home'),
    #path('hello/', views.HelloWorld.as_view(), name='hello_world'),

    #path('google/login/', GoogleLoginView.as_view(), name='google-login'),
    #path('oauth2callback/', OAuth2CallbackView.as_view(), name='oauth2callback'),
    path('send-email/', SendEmailView.as_view(), name='send-email'),
]
