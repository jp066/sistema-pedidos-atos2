from django.db import models

class Comanda(models.Model):
    numero_comanda = models.PositiveIntegerField(unique=True, blank=True, null=True)
    nome = models.CharField(max_length=100)  # Nome da pessoa
    email = models.EmailField(blank=True, null=True)
    servo = models.CharField(max_length=100, blank=True, null=True)
    sem_servo = models.BooleanField(default=False)
    forma_pagamento = models.CharField(max_length=20, choices=[
        ('dinheiro', 'Dinheiro'),
        ('pix', 'Pix'),
        ('cartao', 'Cartão'),
    ])
    pedido = models.CharField(max_length=100)
    pago = models.BooleanField(default=False)
    finalizada = models.BooleanField(default=False)
    data_criacao = models.DateTimeField(auto_now_add=True)

    @classmethod
    def get_total_comandas(cls):
        return cls.objects.count()

    def total(self):
        return sum(item.preco for item in self.itens.all())

    def __str__(self):
        return f"Comanda #{self.id} - {self.nome}"


class Item(models.Model):
    comanda = models.ForeignKey(Comanda, related_name='itens', on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    preco = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.nome} (R$ {self.preco})"