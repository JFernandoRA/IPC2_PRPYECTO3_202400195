from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('configuracion/', views.configuracion, name='configuracion'),
    path('consumo/', views.consumo, name='consumo'),
    path('operaciones/', views.operaciones, name='operaciones'),
    path('consultar/', views.consultar_datos, name='consultar_datos'),
    path('reset/', views.reset_sistema, name='reset_sistema'),
    path('facturacion/', views.facturacion, name='facturacion'),
    path('reportes/', views.reportes, name='reportes'),
    path('ayuda/', views.ayuda, name='ayuda'),  
]