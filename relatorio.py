from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from comandas.models import Comanda
import datetime
import os
from collections import defaultdict

def gerar_pdf_comandas_vendidas(caminho_saida="comandas_vendidas.pdf"):
    comandas = Comanda.objects.all().order_by('-data_criacao')

    vendas_por_servo = defaultdict(int)

    # Contar quantas comandas cada servo vendeu
    for comanda in comandas:
        if comanda.servo:
            vendas_por_servo[comanda.servo] += 1
        elif comanda.sem_servo:
            vendas_por_servo["Sem servo"] += 1
        else:
            vendas_por_servo["---"] += 1

    c = canvas.Canvas(caminho_saida, pagesize=A4)
    largura, altura = A4
    y = altura - 2 * cm

    # Cabeçalho
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2 * cm, y, "Relatório de Comandas Vendidas")
    y -= 1 * cm
    c.setFont("Helvetica", 10)
    c.drawString(2 * cm, y, f"Gerado em: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}")
    y -= 2 * cm

    # Mostrar só a quantidade por servo
    c.setFont("Helvetica-Bold", 14)
    c.drawString(2 * cm, y, "Quantidade de Comandas Vendidas por Servo:")
    y -= 1 * cm

    c.setFont("Helvetica", 12)
    for servo, qtd in vendas_por_servo.items():
        if y <= 2 * cm:
            c.showPage()
            y = altura - 2 * cm
            c.setFont("Helvetica", 12)
        c.drawString(2 * cm, y, f"{servo}: {qtd}")
        y -= 0.8 * cm

    c.save()
    print(f"PDF gerado em: {os.path.abspath(caminho_saida)}")
