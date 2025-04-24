from django.db import models

from django.db import models


class Comanda(models.Model):
    nome = models.CharField(max_length=100)
    servo = models.CharField(max_length=100, blank=True)
    forma_pagamento = models.CharField(max_length=20, choices=[
        ('dinheiro', 'Dinheiro'),
        ('pix', 'Pix'),
        ('cartao', 'Cartão'),
    ])
    pedido = models.CharField(max_length=100)
    pago = models.BooleanField(default=False)

    def total(self):
        return sum(item.preco for item in self.itens.all())



class Item(models.Model):
    comanda = models.ForeignKey(Comanda, related_name='itens', on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    preco = models.DecimalField(max_digits=6, decimal_places=2)

