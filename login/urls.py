from django.urls import path
from .views import registro_api
from .serializers import CustomTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

urlpatterns = [
    path('registro/', registro_api, name='registro_api'),
    path('login/', CustomTokenObtainPairView.as_view(), name='obtenerToken'),

]
