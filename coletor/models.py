from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.
class Host(models.Model):
    url = models.URLField('url')
    count = models.BigIntegerField(validators=[MinValueValidator(0)],default=0)

class Link(models.Model):
    coletado_em = models.DateField('Coletado em:', auto_now=True)
    url = models.URLField('Url')
    host = models.ForeignKey(Host, on_delete=models.CASCADE)

class Documento(models.Model):
    url = models.URLField('Url')
    texto = models.TextField('Texto')
    visao = models.TextField('Visao')
    sequencia_maxima = models.FloatField('Sequência máxima',blank=True, null=True)
    soma_quadrados_pesos = models.FloatField('Soma quadrados dos Pesos', blank=True, null=True)
    link = models.ForeignKey(Link, on_delete=models.CASCADE)

class TermoDocumento(models.Model):
    n = models.BigIntegerField(validators=[MinValueValidator(0)])
    texto = models.TextField('Texto')


class IndiceInvertido(models.Model):
    documento = models.ForeignKey(Documento, on_delete=models.CASCADE)
    termo = models.ForeignKey(TermoDocumento,  on_delete=models.CASCADE)
    frequencia = models.IntegerField(validators=[MinValueValidator(0)])
    peso = models.DecimalField('Peso',max_digits=10, decimal_places=5)
