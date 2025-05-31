from django.urls import path
from . import views

app_name = 'caixa'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('reiniciar/', views.reiniciar, name='reiniciar'),
    path('pagar/<int:pk>/', views.marcar_como_pago, name='marcar_como_pago'),
    path('acesso-token/', views.acessar_caixa_token, name='acessar_token'),
    path('sair/', views.sair_caixa, name='sair_caixa'),
    path('comanda/<int:comanda_id>/finalizar/', views.marcar_como_finalizada, name='marcar_como_finalizada'),

]
