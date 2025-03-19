from django.urls import path
from .views import registro_api
from .serializers import CustomTokenObtainPairView

urlpatterns = [
    path('registro/', registro_api, name='registro_api'),
    path('login/', CustomTokenObtainPairView.as_view(), name='obtenerToken'),
]
