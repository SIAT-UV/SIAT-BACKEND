from django.urls import path
from .views import registro_api, CustomTokenObtainPairView, CustomTokenRefreshView


urlpatterns = [
    path('registro/', registro_api, name='registro_api'),
    path('login/', CustomTokenObtainPairView.as_view(), name='obtenerToken'),
    path('refresh/', CustomTokenRefreshView.as_view(), name='refrescarToken'),
]
