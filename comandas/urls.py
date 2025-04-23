from django.urls import path
from . import views

app_name = 'comandas'

urlpatterns = [
    path('', views.comanda_list, name='comanda_list'),
    path('nova/', views.comanda_create, name='comanda_create'),
    path('pix/<int:pk>/', views.comanda_pix, name='comanda_pix'),
    path('cartao/<int:pk>/', views.comanda_cartao, name='comanda_cartao'),
    path('reiniciar/', views.reiniciar_comandas, name='reiniciar_comandas'),
    path('voucher/<int:pk>/', views.gerar_voucher_view, name='gerar_voucher'),
]