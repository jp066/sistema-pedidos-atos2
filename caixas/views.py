from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import timedelta
from django.conf import settings

from comandas.models import Comanda


@csrf_exempt
def acessar_caixa_token(request):
    if request.method == 'POST':
        token_inserido = request.POST.get('token')
        if token_inserido == settings.CAIXA_TOKEN:
            request.session['acesso_caixa'] = True
            return redirect('caixa:dashboard')
        else:
            return render(request, 'acesso_token.html', {'erro': 'Token inválido'})

    return render(request, 'acesso_token.html')

def token_valido(request):
    return request.GET.get('token') == settings.CAIXA_TOKEN


def dashboard(request):
    if not request.session.get('acesso_caixa'):
        return redirect('caixa:acessar_token')

    # Pegando o termo de pesquisa
    nome_pesquisa = request.GET.get('nome', '')

    # Filtros de comandas
    if nome_pesquisa:
        comandas = Comanda.objects.filter(nome__icontains=nome_pesquisa)
    else:
        comandas = Comanda.objects.all()

    # Verificação de tempo (72h)
    limite = timezone.now() - timedelta(hours=72)

    # Para cada comanda, verificamos se passou das 72 horas
    for comanda in comandas:
        comanda.passou_72h = comanda.data_criacao < limite and not comanda.pago

    total = comandas.count()
    total_pix = comandas.filter(forma_pagamento='pix').count()
    total_cartao = comandas.filter(forma_pagamento='cartao').count()

    context = {
        'comandas': comandas,
        'total': total,
        'total_pix': total_pix,
        'total_cartao': total_cartao,
        'nome_pesquisa': nome_pesquisa
    }
    return render(request, 'caixa_dashboard.html', context)

@csrf_exempt
def reiniciar(request):
    if request.method == 'POST':
        Comanda.objects.all().delete()
    return redirect('caixa:dashboard')


@csrf_exempt
def marcar_como_pago(request, pk):
    comanda = get_object_or_404(Comanda, pk=pk)
    comanda.pago = True  # Atualiza o status para "pago"
    comanda.save()

    # Enviar e-mail de confirmação de pagamento
    assunto = "Pagamento Confirmado - ATOS Burguer"
    mensagem = f"Olá, {comanda.nome}!\n\nSeu pagamento foi confirmado com sucesso para o pedido {comanda.pedido}.\n\nObrigado por sua compra!\n\nEquipe ATOS Burguer"

    if comanda.email:
        send_mail(
            assunto,
            mensagem,
            settings.EMAIL_HOST_USER,
            [comanda.email],
            fail_silently=False,
        )

    return redirect('caixa:dashboard')  # Redireciona para a lista atualizada

@csrf_exempt
def marcar_como_finalizada(request, comanda_id):
    comanda = get_object_or_404(Comanda, id=comanda_id)
    comanda.finalizada = True
    comanda.save()
    return redirect('caixa:dashboard')

@csrf_exempt
def sair_caixa(request):
    if request.session.get('acesso_caixa'):
        del request.session['acesso_caixa']  # Remove a chave da sessão
    return redirect('caixa:acessar_token')