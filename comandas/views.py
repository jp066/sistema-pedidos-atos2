from django.shortcuts import render, redirect, get_object_or_404
from .models import Comanda, Item
from django.db import connection
import os
from django.conf import settings
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from django.http import FileResponse


COMBOS = {
    'Hamburguer + Suco': [
        {'nome': 'Hamburguer', 'preco': 15.00},
        {'nome': 'Suco', 'preco': 5.00},
    ],
    'Hamburguer + Refri': [
        {'nome': 'Hamburguer', 'preco': 15.00},
        {'nome': 'Refrigerante', 'preco': 6.00},
    ],
}
def comanda_list(request):
    return render(request, 'comanda_list.html')


def comanda_create(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        pagamento = request.POST.get('pagamento')
        pedido = request.POST.get('pedido')

        comanda = Comanda.objects.create(
            nome=nome,
            forma_pagamento=pagamento,
            pedido=pedido
        )

        # Cria os itens com base no combo escolhido
        for item in COMBOS.get(pedido, []):
            Item.objects.create(
                comanda=comanda,
                nome=item['nome'],
                preco=item['preco']
            )

        if pagamento == 'pix':
            return redirect('comandas:comanda_pix', pk=comanda.pk)
        elif pagamento == 'cartao':
            return redirect('comandas:comanda_cartao', pk=comanda.pk)
        else:
            return redirect('comandas:comanda_list')

    return render(request, 'comanda_form.html')


def comanda_pix(request, pk):
    comanda = get_object_or_404(Comanda, pk=pk)
    return render(request, 'comanda_pix.html', {'comanda': comanda})

def comanda_cartao(request, pk):
    comanda = get_object_or_404(Comanda, pk=pk)
    return render(request, 'comanda_cartao.html', {'comanda': comanda})


def reiniciar_comandas(request):
    if request.method == 'POST':
        Item.objects.all().delete()
        Comanda.objects.all().delete()

        # Resetar o ID da tabela Comanda
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='comandas_comanda'")

        return redirect('comandas:comanda_list')

    return redirect('comandas:comanda_list')


def gerar_voucher_view(request, pk):
    comanda = get_object_or_404(Comanda, pk=pk)

    # Gera o PDF com base na comanda
    gerar_voucher_comanda(pk)

    # Caminho do arquivo gerado
    caminho_pdf = os.path.join('vouchers', f'voucher_{pk}.pdf')

    return FileResponse(open(caminho_pdf, 'rb'), content_type='application/pdf')


def gerar_voucher_comanda(comanda_id, pasta='vouchers'):
    os.makedirs(pasta, exist_ok=True)

    comanda = Comanda.objects.prefetch_related('itens').get(pk=comanda_id)
    nome_cliente = comanda.nome
    pedido_descricao = comanda.pedido
    numero_comanda = comanda.pk

    nome_arquivo = os.path.join(pasta, f'voucher_{numero_comanda}.pdf')

    largura, altura = 21 * cm, 9 * cm
    c = canvas.Canvas(nome_arquivo, pagesize=(largura, altura))

    # Logo centralizado
    logo_path = os.path.join(settings.BASE_DIR, 'static/img/logo_atos2.png')
    if os.path.exists(logo_path):
        logo = ImageReader(logo_path)
        c.drawImage(logo, (largura - 3.5 * cm) / 2, altura - 4.8 * cm, width=3.5 * cm, height=3.5 * cm, mask='auto')

    # Nome do cliente (substitui "Atos 2")
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(largura / 2, altura - 5.4 * cm, nome_cliente)

    # Descrição do pedido
    c.setFont("Helvetica", 14)
    c.drawCentredString(largura / 2, altura - 6.2 * cm, pedido_descricao)

    # Número da comanda
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(largura / 2, altura - 7.5 * cm, str(numero_comanda))

    c.showPage()
    c.save()
    print(f"Voucher salvo: {nome_arquivo}")