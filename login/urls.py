from django.urls import path
from .views import registro_api  # Importa las vistas de la app

urlpatterns = [
    path('registro/', registro_api, name='registro_api'),
]
