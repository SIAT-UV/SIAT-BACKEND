from django.urls import path
from .views import AccidenteCreateView, AccidenteListView
from .analiticas import *
from .clusterView import ShowHighRiskView
urlpatterns = [
    path('accidentes/', AccidenteCreateView.as_view(), name='accidente-create'),
    path('accidentes/list', AccidenteListView.as_view(), name='accidente-list'),
    path('accidentes/filterByMonth/', FilterAccidentByMonthView.as_view(), name='accidente-filter'),
    path('accidentes/countByMonth/', CountAccidentByMonthView.as_view(), name='accidente-count'),
    path('accidentes/recentlyAccident', RecentlyAccidentView.as_view(), name='accidente-recently'),
    path('accidentes/accidentByType', FilterAccidentByTypeView.as_view(), name='accidente-type'),
    path('accidentes/accidentByService', FilterAccidentByTypeServiceView.as_view(), name='accidente-service'),
    path('accidentes/highRiskIntersection',ShowHighRiskView.as_view(), name='high-risk-intersection'),
    path('accidentes/accidentByUser', AccidentsByUserView.as_view(), name='accidente-user'),
    path('accidentes/accidentByYear', AccidentByYear.as_view(), name='accidente-por-año'),
]
