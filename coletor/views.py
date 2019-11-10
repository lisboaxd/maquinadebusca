
from django.shortcuts import render
from django.views.generic import View
from django.http.response import \
    HttpResponse, \
    JsonResponse, \
    HttpResponseRedirect
from django.urls import reverse
from rest_framework.viewsets import ViewSet, ModelViewSet
from rest_framework.response import Response
from urllib.parse import urlparse


from coletor.serializers import DocumentoSerializer, HostSerializer, LinkSerializer
from coletor.models import \
        Documento, \
        Host, \
        Link,\
        TermoDocumento, \
        IndiceInvertido

from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlsplit
import re, requests, json, time



# Create your views here.

#class ColetorListView(ViewSet):
#    serializer_class = ColetorSerializer
#    queryset = Documento.objects.all()

    

class ColetorView(View):

    def _checkDuplicity(self, url_list):
        return list(set(url_list))
    
    def _linksInRobots(self, url):
        '''
        Retorna set de links no robots.txt do host
        '''
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

    def _verifica_se_existe(self, model, *args, **kw):
        return len(model.objects.filter(**kw)) > 0




    def _coletaUrls(self, url):
        coletado = {}
        host = ''
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
        
        ho, created = Host.objects.get_or_create(url=host)
        if created:
            ho.count = 1
        else:
            ho.count = ho.count + 1
        ho.save()

        #Cria o link coletado no banco, caso exista, retorna ele e atuaza a data de coleta
        time_threshold = datetime.now() - timedelta(minutes=1)
        try:
            li = Link.objects.get(url=url, host=ho, coletado_em__gt=time_threshold)
        except Link.DoesNotExist:
            li = Link(url=url, host=ho)
            li.host=ho
            li.save()
            doc = Documento(url=coletado.get('url'),texto=coletado.get('texto'),visao=coletado.get('visao'),link=li)
            doc.save()
            print('\x1b[2;30;44m DOCUMENTO: ' + url + '\x1b[0m')

        for url in urls:
            try:
                li, created = Link.objects.get_or_create(host=ho,url=url)
                if created:
                    print('\x1b[6;30;42m' + url + '\x1b[0m')
                    continue
                else:
                    print('\x1b[2;30;41m' + url + '\x1b[0m')
            except:
                continue
        print('\x1b[2;30;44m {0}\n{1}\n{0} \x1b[0m'.format('###'*10, coletado.get('url')))
        return coletado

    
    def get (self, request, *args, **kw):
        urls = [
            "http://journals.ecs.soton.ac.uk/java/tutorial/networking/urls/readingWriting.html",
            "https://www.baeldung.com/java-string-remove-stopwords",
            "https://www.youtube.com/watch?v=MGWJbaYdy-Y&list=PLZTjHbp2Y7812axMiHkbXTYt9IDCSYgQz",
            "https://www.guj.com.br/t/verficar-duplicata-num-array-unidimensional/35422/9",
            "http://journals.ecs.soton.ac.uk/java/tutorial/networking/urls/readingWriting.html"
            ]
        if len(request.GET.getlist('urls')) > 0:
            urls = request.GET.getlist('urls')
        context = []
        for url in urls:
            time.sleep(10)
            context.append(self._coletaUrls(url))
        links = Link.objects.filter(coletado_em__lt=datetime.now() - timedelta(minutes=1)).values('url')
        for link in links:
            self._coletaUrls(link.get('url'))
        return HttpResponseRedirect(reverse('iniciar'))


class LinkViewSet(ModelViewSet):
    queryset = Link.objects.all()
    serializer_class = LinkSerializer


class DocumentoViewSet(ModelViewSet):
    queryset = Documento.objects.all()
    serializer_class = DocumentoSerializer


class HostViewSet(ModelViewSet):
    queryset = Host.objects.all()
    serializer_class = HostSerializer
