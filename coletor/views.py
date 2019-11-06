from django.shortcuts import render

from rest_framework.viewsets import ViewSet
from rest_framework.response import Response

from coletor.serializers import ColetorSerializer
from coletor.models import Documento

from urllib.parse import urlparse


# Create your views here.

class ColetorListView(ViewSet):
    serializer_class = ColetorSerializer
    queryset = Documento.objects.all()

    def __init__(self,*args,**kwargs):
        self.urls =  [
            "http://journals.ecs.soton.ac.uk/java/tutorial/networking/urls/readingWriting.html",
            "https://www.baeldung.com/java-string-remove-stopwords",
            "https://www.youtube.com/watch?v=MGWJbaYdy-Y&list=PLZTjHbp2Y7812axMiHkbXTYt9IDCSYgQz",
            "https://www.guj.com.br/t/verficar-duplicata-num-array-unidimensional/35422/9",
            "http://journals.ecs.soton.ac.uk/java/tutorial/networking/urls/readingWriting.html"
            ]
        super().__init__(*args, **kwargs)

    def checkDuplicity(self, *urls):
        clear_urls = []
        for url in urls:
            complete_url = f"{urlparse(url).scheme}://{urlparse(url).hostname}"
            if complete_url not in clear_urls:
                clear_urls.append(complete_url)
        return clear_urls
            

    def checkRobotsDisalow(self, urls):
        import requests, bs4
        # TODO: Terminar stop words com requests e bs4
        for url in urls:
            requests.get(f'{url}/robots.txt')
        

    def list(self, request, *args, **kw):
        aa = self.checkDuplicity(*self.urls)
        
        return Response()
