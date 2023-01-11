from django.urls import path
from .views.bascula.views import *

urlpatterns = [    
    # REPORTES BASCULA    
    path('rpt_bascula001/', RptBascula001ReportView.as_view(), name='rpt_bascula001'),
    path('rpt_bascula002/', RptBascula002ReportView.as_view(), name='rpt_bascula002'),
    path('rpt_bascula003/', RptBascula003ReportView.as_view(), name='rpt_bascula003'),
    path('rpt_bascula004/', RptBascula004ReportView.as_view(), name='rpt_bascula004'),
    path('rpt_bascula005/', RptBascula005ReportView.as_view(), name='rpt_bascula005'),
    path('rpt_bascula006/', RptBascula006ReportView.as_view(), name='rpt_bascula006'),
    path('rpt_bascula007/', RptBascula007ReportView.as_view(), name='rpt_bascula007'),
    path('rpt_bascula008/', RptBascula008ReportView.as_view(), name='rpt_bascula008'),

]