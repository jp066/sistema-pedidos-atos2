from django.shortcuts import render, redirect, get_object_or_404
from .models import Comanda, Item
from django.db import connection
import os
from django.conf import settings
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from django.http import FileResponse
from reportlab.lib import colors
from django.contrib import messages


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

SERVOS = [
    "João Pedro",
    "Lucas",
    "Antonio Carlos",
    "David",
    "Eva",
    "ingrid",
    "João Lucas",
    "Lauro",
    "Letícia Antunes",
    "Tamyres",
    "Mariana",
    "João Vitor Sabino",
    "Vitória",
    "Márcio Santiago"
]
def comanda_list(request):
    return render(request, 'comanda_list.html')


def comanda_create(request):
    if request.method == 'POST':
        nome      = request.POST.get('nome')
        servo     = request.POST.get('servo')
        sem_servo = request.POST.get('sem_servo') == 'on'
        pagamento = request.POST.get('pagamento')
        pedido    = request.POST.get('pedido')

        # Limite de 2 comandas no total
        if Comanda.objects.count() >= 200:
            return render(
                request,
                'comanda_form.html',
                {
                    'erro_estoque': 'O estoque de comandas está esgotado. Não é possível criar mais comandas.'
                }
            )

        if sem_servo:
            servo = ''

        if not sem_servo and Comanda.objects.filter(servo=servo).count() >= 3:
            return render(
                request,
                'comanda_form.html',
                {
                    'erro_servo': f'{servo} já vendeu todas as comandas.'
                }
            )

        # Cria a comanda
        comanda = Comanda.objects.create(
            nome=nome,
            servo=servo,
            sem_servo=sem_servo,
            forma_pagamento=pagamento,
            pedido=pedido
        )

        # Cria itens do combo selecionado
        for item in COMBOS.get(pedido, []):
            Item.objects.create(
                comanda=comanda,
                nome=item['nome'],
                preco=item['preco']
            )

        # Redireciona conforme pagamento
        if pagamento == 'pix':
            return redirect('comandas:comanda_pix', pk=comanda.pk)
        elif pagamento == 'cartao':
            return redirect('comandas:comanda_cartao', pk=comanda.pk)
        else:
            return redirect('comandas:comanda_list')

    # GET → exibe formulário
    return render(request, 'comanda_form.html', {
        'servos': SERVOS})




def comanda_pix(request, pk):
    comanda = get_object_or_404(Comanda, pk=pk)

    if comanda.pago:
        messages.info(request, 'Obrigado por sua compra!')
        return redirect('comandas:comanda_list')

    return render(request, 'comanda_pix.html', {'comanda': comanda})


def comanda_cartao(request, pk):
    comanda = get_object_or_404(Comanda, pk=pk)

    if comanda.pago:
        messages.info(request, 'Obrigado por sua compra!')
        return redirect('comandas:comanda_list')

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
    nome_cliente   = comanda.nome
    servo_cliente  = comanda.servo if not comanda.sem_servo else 'Comprada no local'  # Verifica se é sem servo
    pedido_descricao = comanda.pedido
    numero_comanda = comanda.pk
    status_pago    = "PAGO" if comanda.pago else "NÃO PAGO"

    nome_arquivo = os.path.join(pasta, f'voucher_{numero_comanda}.pdf')

    largura, altura = 21 * cm, 9 * cm
    c = canvas.Canvas(nome_arquivo, pagesize=(largura, altura))

    # Logo
    logo_path = os.path.join(settings.BASE_DIR, 'static/img/logo_atos2.png')
    if os.path.exists(logo_path):
        logo = ImageReader(logo_path)
        c.drawImage(logo, (largura - 3.5 * cm) / 2,
                    altura - 4.2 * cm, width=3.5 * cm, height=3.5 * cm, mask='auto')

    # Nome do cliente
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(largura / 2, altura - 4.8 * cm, nome_cliente)

    # Nome do servo (ou "Comprada no local" se for sem_servo)
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(largura / 2, altura - 5.5 * cm, f"Servo: {servo_cliente}")

    # Pedido
    c.setFont("Helvetica", 14)
    c.drawCentredString(largura / 2, altura - 6.2 * cm, pedido_descricao)

    # Número da comanda
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(largura / 2, altura - 7.5 * cm, str(numero_comanda))

    # Status
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(colors.green if comanda.pago else colors.red)
    c.drawCentredString(largura / 2, altura - 8.4 * cm, status_pago)
    c.setFillColor(colors.black)

    # --- QR Code Pix ---
    qr_path = os.path.join(settings.BASE_DIR, 'static/img/qr_code.jpeg')
    if os.path.exists(qr_path):
        qr = ImageReader(qr_path)
        qr_width, qr_height = 2.5 * cm, 2.5 * cm
        c.drawImage(qr, largura - qr_width - 1 * cm, 0.5 * cm,
                    width=qr_width, height=qr_height, mask='auto')

    c.showPage()
    c.save()
    print(f"Voucher salvo: {nome_arquivo}")
