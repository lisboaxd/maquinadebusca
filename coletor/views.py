
from django.db.models import Q
from django.shortcuts import render
from django.utils import timezone
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
from maquinadebusca.settings import BASE_DIR

from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlsplit
import re, requests, json, time



# Create your views here.

#class ColetorListView(ViewSet):
#    serializer_class = ColetorSerializer
#    queryset = Documento.objects.all()

    

class ColetorView(View):


    def _obtem_host(self, url):
        return "{0.scheme}://{0.netloc}".format(urlsplit(url))

    def _remove_duplicados(self, url_list):
        return list(set(url_list))
    
    def _links_no_robots(self, url):
        '''
        Retorna set de links no robots.txt do host
        '''
        host = self._obtem_host(url)
        robots = requests.get(f'{host}/robots.txt').content.decode('utf-8')
        robots = ''.join(re.findall('Disallow:\s/[a-zA-Z0-9/*_&?\-\.]+', robots))
        robots = re.sub(r'Disallow:\s', '@'+host, robots)
        robots = re.split('@', robots)
        return set(robots)
    
    def _recupera_links(self, url, links):
        clean_links = []
        for link in links:
            if not bool(re.match('javascript|#', link.get('href'))):
                clean_links.append(urljoin(url,link.get('href')))
        return set(clean_links)

    def _verifica_se_existe(self, model, *args, **kw):
        return len(model.objects.filter(**kw)) > 0

    def _remove_stopwords(self, texto):        
        file = open(BASE_DIR+'/stopwords.txt','r')
        stopwords = file.readlines()
        file.close()
        stopwords = ''.join(stopwords).split('\n')
        regex = ' | '.join(stopwords)
        texto = texto.lower().rstrip()
        texto = re.sub(regex,'',texto)
        return texto
    
    def tempo_passado(self, hora=0, minuto=0):
        return datetime.now(tz=timezone.utc) - timedelta(hours=hora,minutes=minuto)

    def _coleta(self, url):
        
        try:
            host = self._obtem_host(url)
            robots = self._links_no_robots(url)
            pagina = requests.get(url)
            
            soup = BeautifulSoup(pagina.content, 'html.parser')
            links = soup.find_all('a', href=True)
            texto = soup.prettify()
            visao = self._remove_stopwords(soup.get_text())

            clean_links = self._recupera_links(host,links)
            urls = list(clean_links - robots)
            return {
                'url':url,
                'texto':texto,
                'visao':visao,
                'urls':urls
            }
        except Exception as e:
            return False

    def salva_host(self, url):
        host = self._obtem_host(url)
        ho, created = Host.objects.get_or_create(url=host)
        if created:
                ho.count = 1
        else:
            ho.count = ho.count + 1
        ho.save()
        return ho

    def salva_link(self, url, host, tempo_tolerancia=2):
        if type(host) == str:
            host = Host.objects.get(url=host)
        time_threshold = self.tempo_passado(hora=tempo_tolerancia)
        li = ''
        try:
            li = Link.objects.get(url=url, host=host, coletado_em__gt=time_threshold)
        except Link.DoesNotExist:
            li = Link(url=url, host=host)
            li.host=host
            li.save()
            doc = Documento(url=coletado.get('url'),texto=coletado.get('texto'),visao=coletado.get('visao'),link=li)
            doc.save()
            print('\x1b[2;30;44m DOCUMENTO: ' + url + '\x1b[0m')
        return li
    
    
    def _coleta_urls(self, url):

        #refatorar
        coletado = self._coleta(url)
        host = self._obtem_host(url)
        obj_host = self.salva_host(url)
       

        #Cria o link coletado no banco, caso exista, retorna ele e atuaza a data de coleta
        li = self.salva_link(url, host)

        for url in coletado.get('urls'):
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

    def links_para_coletar(self):
        urls = Link.objects.filter(coletado_em__lt=self.tempo_passado(hora=2)).values('url')
        if not urls:
            return [
                {'url':"http://journals.ecs.soton.ac.uk/java/tutorial/networking/urls/readingWriting.html"},
                {'url':"https://www.baeldung.com/java-string-remove-stopwords"},
                {'url':"https://www.youtube.com/watch?v=MGWJbaYdy-Y&list=PLZTjHbp2Y7812axMiHkbXTYt9IDCSYgQz"},
                {'url':"https://www.guj.com.br/t/verficar-duplicata-num-array-unidimensional/35422/9"},
                {'url':"http://journals.ecs.soton.ac.uk/java/tutorial/networking/urls/readingWriting.html"}
            ]
        return urls


    def get (self, request, *args, **kw):
        links = self.links_para_coletar()
        #loop eterno nos mesmos links
        for link in links:
            self._coleta_urls(link.get('url'))
            time.sleep(10)
        return HttpResponseRedirect(reverse('iniciar'))
    
    # def post (self, request, *args, **kw):
    #     from django.db import IntegrityError
    #     from django.core.serializers import serialize
    #     response = []

    #     try:
    #         urls = json.loads(request.body)
    #         print(urls)
    #         for url in urls:
    #             print(url)
    #             try:
    #                 response.append(self._coleta_urls(url.get('url')))
    #             except IntegrityError as e:
    #                 response.append({
    #                     'tipoe':'erro',
    #                     'texto': f'{url} já foi cadastrada anteriormente'
    #                     })
    #     except Exception as e:
    #         print(f'Erro ao processar requisição: {e}')
    #     return JsonResponse(response, safe=False)

        
    


class LinkViewSet(ModelViewSet):
    queryset = Link.objects.all()
    serializer_class = LinkSerializer


class DocumentoViewSet(ModelViewSet):
    queryset = Documento.objects.all()
    serializer_class = DocumentoSerializer


class HostViewSet(ModelViewSet):
    queryset = Host.objects.all()
    serializer_class = HostSerializer
