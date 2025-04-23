from django.shortcuts import render, redirect, get_object_or_404
from comandas.models import Comanda

def dashboard(request):
    comandas = Comanda.objects.filter(pago=False)
    total = comandas.count()
    total_pix = comandas.filter(forma_pagamento='pix').count()
    total_cartao = comandas.filter(forma_pagamento='cartao').count()

    context = {
        'comandas': comandas,
        'total': total,
        'total_pix': total_pix,
        'total_cartao': total_cartao,
    }
    return render(request, 'caixa_dashboard.html', context)

def reiniciar(request):
    if request.method == 'POST':
        Comanda.objects.all().delete()
    return redirect('caixa:dashboard')


def finalizar_pedido(request, pk):
    comanda = get_object_or_404(Comanda, pk=pk)
    comanda.status = 'feito'
    comanda.save()
    return redirect('caixa:dashboard')


def marcar_como_pago(request, pk):
    comanda = get_object_or_404(Comanda, pk=pk)
    comanda.pago = True  # <--- usar o campo booleano existente
    comanda.save()
    return redirect('caixa:dashboard')  # Redireciona para a lista atualizada