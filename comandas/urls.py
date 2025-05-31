from django.urls import path
from . import views
from .views import vendas_por_servo_pdf

app_name = 'comandas'

urlpatterns = [
    path('', views.comanda_list, name='comanda_list'),
    path('nova/', views.comanda_create, name='comanda_create'),
    path('pix/<int:pk>/', views.comanda_pix, name='comanda_pix'),
    path('cartao/<int:pk>/', views.comanda_cartao, name='comanda_cartao'),
    path('reiniciar/', views.reiniciar_comandas, name='reiniciar_comandas'),
    path('voucher/<int:pk>/', views.gerar_voucher_view, name='gerar_voucher'),
    path('excluir_comanda/<int:pk>/', views.excluir_comanda, name='excluir_comanda'),
    path('buscar-comanda/', views.buscar_comanda_por_nome, name='buscar_comanda'),
    path('relatorio/vendas-por-servo/', vendas_por_servo_pdf, name='vendas_por_servo_pdf'),
    path('validar-servo/<int:pk>/', views.validar_servo, name='validar_servo'),
]