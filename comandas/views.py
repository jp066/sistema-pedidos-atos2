from datetime import timedelta
from django.db.models.aggregates import Max
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

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
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.core.mail import send_mail
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from .models import Comanda
from django.db.models import Count


COMBOS = {
    'Hamburguer + Suco': [
        {'nome': 'Hamburguer', 'preco': 17.00},
        {'nome': 'Suco', 'preco': 5.00},
    ],
    'Hamburguer + Refri': [
        {'nome': 'Hamburguer', 'preco': 17.00},
        {'nome': 'Refrigerante', 'preco': 5.00},
    ],
}

SERVOS = [
    "comprada no local",
    "João Pedro Matos",
    "Lucas Eduardo",
    "Antonio Carlos",
    "David",
    "Eva",
    "ingrid",
    "João Lucas",
    "Lauro ",
    "Letícia Antunes",
    "Tamyres",
    "Mariana",
    "João Vitor Sabino",
    "Vitória",
    "Márcio Santiago",
    "João Vitor",
    "Michelle",
    "Danilo",
    "Caio Fontinele",
    "Clara Luzia",
    "Mirelle",
    "Laryssa",
    "Gabriella",
    "Kel ",
    "Kelvin",
    "João guilherme",
    "Rafael Ferro",
    "Leonardo",
    "João Pedro Eloi",
    "Maria Julia",
    "Kel",
    "Vinicius",
    "Maria Vitoria",
    "Beatriz",
    "Rayane",
    "Adriele",
    "Alysson",
    "Amélia",
    "Ana Castro",
    "Clara Sousa",
    "Daiene",
    "Elissandra",
    "Esdras Emanuel",
    "Francisco Lucas",
    "Jerlliany",
    "Keynara",
    "Luis Felipe",
    "Maria Aparecida",
    "Dário",
    "Ariane"
]
def comanda_list(request):
    comandas = Comanda.objects.all()
    if settings.MANUNT == True:
        return render(request, 'Manutencao.html')
    else:
        return render(request, 'comanda_list.html', {'comandas': comandas})

@csrf_exempt
def buscar_comanda_por_nome(request):
    nome_pesquisa = request.GET.get('nome', '')

    if nome_pesquisa:
        comandas = Comanda.objects.filter(nome__icontains=nome_pesquisa)
    else:
        comandas = None

    context = {
        'comandas': comandas,
        'nome_pesquisa': nome_pesquisa,
        'servos': SERVOS,
    }
    return render(request, 'buscar_comanda.html', context)


@require_POST
@csrf_exempt
def validar_servo(request, pk):
    comanda = get_object_or_404(Comanda, pk=pk)

    # Dados do formulário
    servo_informado = request.POST.get('servo', '').strip().lower()
    email_informado = request.POST.get('email', '').strip().lower()
    sem_servo = request.POST.get('sem_servo') == 'on'

    # Dados da comanda
    servo_cadastrado = (comanda.servo or '').strip().lower()
    email_cadastrado = (comanda.email or '').strip().lower()

    # Se a checkbox "sem_servo" estiver marcada, forçamos o valor correspondente
    if sem_servo:
        servo_informado = 'comprada no local'

    # Validação
    if servo_informado == servo_cadastrado and email_informado == email_cadastrado:
        return redirect('comandas:gerar_voucher', pk=pk)
    else:
        messages.error(request, 'Validação encerrada: servo ou e-mail incorreto.')
        return redirect('comandas:buscar_comanda')


def proximo_numero_disponivel():
    usados = set(Comanda.objects.values_list('numero_comanda', flat=True))
    for i in range(1, 201):
        if i not in usados:
            return i
    return None

@csrf_exempt
def comanda_create(request):
    if request.method == 'POST':
        nome      = request.POST.get('nome')
        email     = request.POST.get('email')  # Novo campo no form!
        servo     = request.POST.get('servo')
        sem_servo = request.POST.get('sem_servo') == 'on'
        pagamento = request.POST.get('pagamento')
        pedido    = request.POST.get('pedido')

        # Limite total de comandas
        if Comanda.objects.count() >= 200:
            return render(
                request,
                'comanda_form.html',
                {
                    'erro_estoque': 'O estoque de comandas está esgotado. Não é possível criar mais comandas.'
                }
            )

        # Limite de comandas por servo
        if sem_servo:
            servo = ''
        else:
            comanda_count = Comanda.objects.filter(servo=servo).count()
            if comanda_count == 3:
                messages.success(request, f'{servo} já vendeu 3 comandas! Parabéns pelo esforço! 🎉')

        ultimo_numero = Comanda.objects.aggregate(Max('numero_comanda'))['numero_comanda__max'] or 0
        proximo_numero = ultimo_numero + 1

        comanda = Comanda.objects.create(
            numero_comanda=proximo_numero,
            nome=nome,
            email=email,
            servo=servo,
            sem_servo=sem_servo,
            forma_pagamento=pagamento,
            pedido=pedido
        )

        # Cria os itens baseados no combo escolhido
        for item in COMBOS.get(pedido, []):
            Item.objects.create(
                comanda=comanda,
                nome=item['nome'],
                preco=item['preco']
            )

        # ✉️ Envio do e-mail de confirmação
        assunto = "Pedido realizado no ATOS Burguer"
        mensagem = f"Olá, {nome}!\n\nSeu pedido foi registrado com sucesso:\n\nPedido: {pedido}\nForma de pagamento: {pagamento}\n\nObrigado por escolher o ATOS Burguer!"

        if email:
            try:
                send_mail(
                    assunto,
                    mensagem,
                    settings.EMAIL_HOST_USER,
                    [email],
                    fail_silently=False,
                )
                messages.success(request, 'E-mail de confirmação enviado com sucesso! 🎉')
            except Exception as e:
                print(f"Erro ao enviar o e-mail: {e}")  # Log do erro
                messages.error(request, 'Erro ao enviar o e-mail de confirmação. Tente novamente mais tarde.')  # Exibe erro no popup

        # 🔔 Verifica se existem comandas atrasadas e envia lembrete
        limite = timezone.now() - timedelta(hours=48)
        comandas_atrasadas = Comanda.objects.filter(pago=False, data_criacao__lt=limite)

#        for c in comandas_atrasadas:
#            if c.email:
#                try:
#                    send_mail(
#                        "⏰ Lembrete: pagamento pendente no ATOS Burguer",
#                        f"Olá {c.nome}, notamos que seu pedido feito em {c.data_criacao.strftime('%d/%m/%Y %H:%M')} ainda não foi pago.\n\nSe precisar de ajuda ou quiser cancelar, entre em contato conosco.",
#                        settings.EMAIL_HOST_USER,
#                        [c.email],
#                        fail_silently=False,
#                    )
#                except Exception as e:
#                    print(f"Erro ao enviar o lembrete de pagamento: {e}")  # Log do erro
#                    messages.error(request, f"Erro ao enviar lembrete de pagamento para {c.nome}.")  # Exibe erro no popup

        # 🔁 Redireciona para a página de pagamento apropriada
        if pagamento == 'pix':
            return redirect('comandas:comanda_pix', pk=comanda.pk)
        elif pagamento == 'cartao':
            return redirect('comandas:comanda_cartao', pk=comanda.pk)
        else:
            return redirect('comandas:comanda_list')

    # GET → exibe formulário
    return render(request, 'comanda_form.html', {
        'servos': SERVOS
    })

@csrf_exempt
def excluir_comanda(request, pk):
    if request.method == 'POST':
        try:
            comanda = Comanda.objects.get(pk=pk)

            # Excluir os itens relacionados
            Item.objects.filter(comanda=comanda).delete()

            # Excluir a comanda
            comanda.delete()

            # ⚠️ Resetar o ID da tabela SÓ se não houver mais comandas
            if Comanda.objects.count() == 0:
                with connection.cursor() as cursor:
                    cursor.execute("DELETE FROM sqlite_sequence WHERE name='comandas_comanda'")

        except Comanda.DoesNotExist:
            pass  # ou pode exibir uma mensagem se quiser

        return redirect('caixa:dashboard')

    return redirect('caixa:dashboard')


def comanda_pix(request, pk):
    comanda = get_object_or_404(Comanda, pk=pk)
    comanda_count = Comanda.objects.filter(servo=comanda.servo).count()

    if comanda.pago:
        messages.info(request, 'Obrigado por sua compra!')
        return redirect('comandas:comanda_list')

    return render(request, 'comanda_pix.html', {'comanda': comanda, 'comanda_count': comanda_count})


def comanda_cartao(request, pk):
    comanda = get_object_or_404(Comanda, pk=pk)
    comanda_count = Comanda.objects.filter(servo=comanda.servo).count()

    if comanda.pago:
        messages.info(request, 'Obrigado por sua compra!')
        return redirect('comandas:comanda_list')

    return render(request, 'comanda_cartao.html', {'comanda': comanda, 'comanda_count': comanda_count})


def enviar_email_pagamento_confirmado(comanda):
    nome_cliente = comanda.nome
    email_cliente = comanda.email
    numero_comanda = comanda.numero_comanda

    assunto = "Pagamento Confirmado - ATOS Burguer"
    mensagem = f"Olá, {nome_cliente}!\n\nSeu pagamento foi confirmado e seu pedido foi finalizado com sucesso!\n\nNúmero da Comanda: {numero_comanda}\n\nObrigado por escolher o ATOS Burguer!"

    if email_cliente:
        send_mail(
            assunto,
            mensagem,
            settings.EMAIL_HOST_USER,
            [email_cliente],
            fail_silently=False,
        )

@csrf_exempt
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
    servo_cliente = comanda.servo if not comanda.sem_servo else 'Comprada no local'  # Verifica se é sem servo
    pedido_descricao = comanda.pedido
    numero_comanda = comanda.pk
    status_pago = "PAGO" if comanda.pago else "NÃO PAGO"

    # Dicionário com os preços dos pedidos
    precos_pedido = {
        "Hamburguer + Suco": 22.00,
        "Hamburguer + Refri": 22.00,
    }
    preco_pedido = precos_pedido.get(pedido_descricao, 0.00)

    nome_arquivo = os.path.join(pasta, f'voucher_{numero_comanda}.pdf')

    largura, altura = 21 * cm, 9 * cm
    c = canvas.Canvas(nome_arquivo, pagesize=(largura, altura))

    # Logo
    # Logo
    logo_path = os.path.join(settings.BASE_DIR, 'static/img/logo_atos2.png')
    if os.path.exists(logo_path):
        logo = ImageReader(logo_path)
        c.drawImage(logo, (largura - 3.5 * cm) / 2, altura - 4.2 * cm,
                    width=3.5 * cm, height=3.5 * cm, mask='auto')

    # Nome do cliente
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(largura / 2, altura - 4.8 * cm, nome_cliente)

    # Nome do servo
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(largura / 2, altura - 5.5 * cm,
                        f"Servo: {servo_cliente}")

    # Pedido
    c.setFont("Helvetica", 14)
    c.drawCentredString(largura / 2, altura - 6.2 * cm,
                        f"{pedido_descricao} | R$ {preco_pedido:.2f}")

    # Chave PIX (centralizada e visível)
    c.setFont("Helvetica", 12)
    c.drawCentredString(largura / 2, altura - 7.0 * cm,
                        "Chave PIX: atos2psje@gmail.com")

    # Número da comanda
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(largura / 2, altura - 7.8 * cm, str(numero_comanda))

    # Status de pagamento
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(colors.green if comanda.pago else colors.red)
    c.drawCentredString(largura / 2, altura - 8.6 * cm, status_pago)
    c.setFillColor(colors.black)  # reset color

    # QR Code - alinhado no canto inferior esquerdo
    qr_path = os.path.join(settings.BASE_DIR, 'static/img/qr_code.jpeg')
    if os.path.exists(qr_path):
        qr = ImageReader(qr_path)
        qr_width, qr_height = 2.5 * cm, 2.5 * cm
        c.drawImage(qr, 1 * cm, 1 * cm, width=qr_width, height=qr_height, mask='auto')

    c.showPage()
    c.save()
    print(f"Voucher salvo: {nome_arquivo}")

@csrf_exempt
def vendas_por_servo_pdf(request):
    # Query: pega a quantidade de comandas por servo
    vendas = Comanda.objects.values('servo').annotate(total_vendas=Count('id')).order_by('servo')

    # Response com conteúdo PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="vendas_por_servo.pdf"'

    # Cria o PDF
    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    # Título
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, height - 50, "Relatório de Vendas por Servo")

    # Cabeçalho da tabela
    p.setFont("Helvetica-Bold", 12)
    p.drawString(100, height - 80, "Servo")
    p.drawString(300, height - 80, "Quantidade de Vendas")

    # Conteúdo
    y = height - 100
    p.setFont("Helvetica", 12)
    for venda in vendas:
        servo = venda['servo'] if venda['servo'] else 'Sem Servo'
        total = venda['total_vendas']
        p.drawString(100, y, str(servo))
        p.drawString(300, y, str(total))
        y -= 20
        if y < 50:  # cria nova página se necessário
            p.showPage()
            y = height - 50

    p.save()
    return response