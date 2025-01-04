"""
URL configuration for exchange_api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from api.views import (
    EventList, CurrencyList, UserAuthentication, 
    PasswordResetRequest, PasswordResetConfirm, UsersList, ClearAll, isSuperAdmin, testRenderResetTemplateUi
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from api.serializers import CustomTokenObtainPairSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/events', EventList.as_view()),
    path('api/v1/events/<int:pk>', EventList.as_view(), name='event-detail'),
    path('api/v1/currencies', CurrencyList.as_view()),
    path('api/v1/currencies/<str:currency_name>', CurrencyList.as_view(), name='currency-detail'),
    path('api/v1/authenticate', UserAuthentication.as_view()),
    path('api/v1/users', UsersList.as_view(), name='users'),
    path('api/v1/users/<str:username>', UsersList.as_view(), name='user-detail'),
    path('api/v1/password-reset', PasswordResetRequest.as_view(), name='password_reset'),
    path('reset-password/<str:uidb64>/<str:token>', 
         PasswordResetConfirm.as_view(), name='password_reset_confirm'),
    path('api/v1/clear-all', ClearAll.as_view(), name='clearr-all'),
    path('api/v1/super-user-check/<str:username>', isSuperAdmin.as_view(), name='is-super-admin'),
    path('api/v1/test-reset-template', testRenderResetTemplateUi.as_view(), name='test-reset-template'),
    path('api/v1/token', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
]

