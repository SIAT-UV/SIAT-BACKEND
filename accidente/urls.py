from django.urls import path
from .views import AccidenteCreateView

urlpatterns = [
    path('accidentes/', AccidenteCreateView.as_view(), name='accidente-create'),
]
