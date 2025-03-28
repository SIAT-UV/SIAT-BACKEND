from django.urls import path
from .views import AccidenteCreateView
from .analiticas import *
urlpatterns = [
    path('accidentes/', AccidenteCreateView.as_view(), name='accidente-create'),
    path('accidentes/filterByMonth/', FilterAccidentByMonthView.as_view(), name='accidente-filter'),
    path('accidentes/countByMonth/', CountAccidentByMonthView.as_view(), name='accidente-count'),
    path('accidentes/recentlyAccident', RecentlyAccidentView.as_view(), name='accidente-recently'),
    path('accidentes/accidentByType', FilterAccidentByTypeView.as_view(), name='accidente-type'),
    path('accidentes/accidentByService', FilterAccidentByTypeServiceView.as_view(), name='accidente-service'),
]
