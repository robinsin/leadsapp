
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt import views as jwt_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('user_api.urls')),
    #path('api/', include('user_api.urls')),  # Include your app's URL patterns
    #path('capi/', include('contacts.urls')),
    #path('', include('user_api.urls')),
    #path('hello/', include('myapi.urls')),
    path('token/', jwt_views.TokenObtainPairView.as_view(), name ='token_obtain_pair'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name ='token_refresh'),
    #path('api/', include('chatbot.urls')),
    #path('api/', include('chatbotx.urls')),
    #path('api/ld/', include('leads.urls')),
    #path('', include('google_auth.urls')),
    #path('api/ld-group/', include('email_config.urls')),
    path('api/ld-group/', include('leads_group.urls')),
    
]
