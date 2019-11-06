from django.db import models

# Create your models here.

class Documento(models.Model):
    url = models.URLField('Url')
    texto = models.TextField('Texto')
    visao = models.TextField('Visao')
    sequencia_maxima = models.FloatField('Sequência máxima')
    soma_quadrados_pesos = models.FloatField('Soma quadrados dos Pesos')
