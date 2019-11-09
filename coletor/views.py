
from django.shortcuts import render
from django.views.generic import View
from django.http.response import HttpResponse, JsonResponse
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from urllib.parse import urlparse


from coletor.serializers import ColetorSerializer
from coletor.models import Documento, \
        Host, \
        Link,\
        TermoDocumento, \
        IndiceInvertido

from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlsplit
import re, requests, json



# Create your views here.

class ColetorListView(ViewSet):
    serializer_class = ColetorSerializer
    queryset = Documento.objects.all()

    

class ColetorView(View):

    def _checkDuplicity(self, url_list):
        return list(set(url_list))
    
    def _linksInRobots(self, url):
        host = "{0.scheme}://{0.netloc}".format(urlsplit(url))
        robots = requests.get(f'{host}/robots.txt').content.decode('utf-8')
        robots = ''.join(re.findall('Disallow:\s/[a-zA-Z0-9/*_&?\-\.]+', robots))
        robots = re.sub(r'Disallow:\s', '@'+host, robots)
        robots = re.split('@', robots)
        return host, set(robots)
    
    def _recuperaLinks(self, url, links):
        clean_links = []
        for link in links:
            if not bool(re.match('javascript|#', link.get('href'))):
                clean_links.append(urljoin(url,link.get('href')))
        return set(clean_links)



    def _coletaUrls(self, url):
        coletado = {}
        try:
            host , robots = self._linksInRobots(url)
            pagina = requests.get(url)
            
            soup = BeautifulSoup(pagina.content, 'html.parser')
            links = soup.find_all('a', href=True)
            texto = soup.prettify()
            visao = soup.get_text()

            clean_links = self._recuperaLinks(host,links)
            urls = list(clean_links - robots)
            coletado = {
                'url':url,
                'texto':texto,
                'visao':visao,
                'urls':urls
            }
        except Exception as e:
            print('ERRO: {0}'.format(e))
        ho = Host(url=host)
        ho.count += 1
        ho.save()
        li = Link(
            url='url',
            host=ho,
        )
        li.save()
        doc = Documento(
            url=url,
            texto=texto,
            visao=visao,
            link=li
        )
        doc.save()

        for url in urls:
            Link(host=ho,url=url).save()
        return coletado

    
    def get (self, request, *args, **kw):
        urls = [
            #"http://journals.ecs.soton.ac.uk/java/tutorial/networking/urls/readingWriting.html",
            #"https://www.baeldung.com/java-string-remove-stopwords",
            "https://www.youtube.com/watch?v=MGWJbaYdy-Y&list=PLZTjHbp2Y7812axMiHkbXTYt9IDCSYgQz",
            #"https://www.guj.com.br/t/verficar-duplicata-num-array-unidimensional/35422/9",
            #"http://journals.ecs.soton.ac.uk/java/tutorial/networking/urls/readingWriting.html"
            ]
        context = []
        for url in urls:
            context.append(self._coletaUrls(url))
        return JsonResponse(context, safe=False)
