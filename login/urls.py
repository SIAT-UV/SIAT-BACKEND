from django.urls import path
from .views import registro_api, CustomTokenObtainPairView, CustomTokenRefreshView, PasswordResetRequestView, PasswordResetConfirmView, LogoutView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('registro/', registro_api, name='registro_api'),
    path('login/', CustomTokenObtainPairView.as_view(), name='obtenerToken'),
    path('refresh/', CustomTokenRefreshView.as_view(), name='refrescarToken'),
    path('password-reset/request/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
