from django.urls import path
from . import views

app_name = 'caixa'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('reiniciar/', views.reiniciar, name='reiniciar'),
    path('pagar/<int:pk>/', views.marcar_como_pago, name='marcar_como_pago'),

]
