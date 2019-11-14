from sqlalchemy import text

from src.model.models import Documento, DocumentoLink, IndiceInvertido
from src.service.database import db_session


class IndexadorService:
    termos = []
    documentos = []
    def limpaCriaIndice(self):
        self.termos = []
        inds.deleteAllNativeQuery()
        ts.deleteAllNativeQuery()
        return self.criaIndice()

    def criaIndice(self):
        self.documentos = ds.listAll()
        for documento in self.documentos:
            try:
                print('Processando indice doc.id: ['+str(documento.id)+']')
                documento.frequenciaMaxima = 0
                documento.somaQuadradosPesos = 0
                documento = ds.save(documento)
                self.indexar(documento, len(self.documentos))
            except Exception:
                print('Falha ao indexar o documento id:[' + documento.id + ']')
                return False
        return True

    def indexar(self, documento, N):
        termos = documento.visao.split()
        count = 1
        for word in termos:
            if(word is not None and word != ''):
                print('processando palavra [' + word + '] - '+str(count)+'/'+str(len(termos)))
                termo = TermoDocumento()
                termo = self.getTermo(word)
                f = self.frequencia(termo.texto, termos)
                if f > documento.frequenciaMaxima:
                    documento.frequenciaMaxima = f
                peso = self.calcularPeso(N, termo.n, f)
                documento.adicionarPeso(peso)
                inds.inserirEntradaIndiceInvertido(termo, documento, f, peso)
            count = count+1

    def getTermo(self, word):
        try:
            termo = ts.findByTermo(word)
            termo.n = self.quantDocPorTermo(word)
            termo = ts.update(termo)
            return termo
        except Exception:
            termo = TermoDocumento()
            termo.texto = word
            termo.n = self.quantDocPorTermo(word)
            termo = ts.save(termo)
            self.termos.append(termo)
            return termo

    def quantDocPorTermo(self, word):
        n = 0
        for documento in self.documentos:
            try:
                visaoArray = documento.visao.split()
                indice = visaoArray.index(word)
                n = n+1
            except Exception:
                continue
        return n

    def frequencia(self, texto, termos):
        contador = 0
        i = 0
        while i < len(termos):
            if(termos[i] is not None and termos[i] != " "):
                if termos[i] == texto:
                    contador = contador+1
                    termos[i] = ""
            i = i+1
        return contador

    def getDocumentos(self):
        return self.documentos

    def calcularPeso(self, N, n, f):
        tf = self.cacularTf(f)
        idf = self.calcularIdf(N, n)
        return tf*idf

    def cacularTf(self, f):
        if f == 0:
            return 0
        return 1 + self.log(f, 2)

    def log(self, x, base):
        a = math.log(x)
        b = math.log(base)
        if a == 0 or b == 0:
            return 0
        return a/b

    def calcularIdf(self, N, n):
        if N == 0 or n == 0:
            return 0
        return self.log((N / n), 2)


class IndiceInvertidoService:
    
    def listAll(self):
        return IndiceInvertido.query.all()

    def findById(self, id):
        return IndiceInvertido.query.filter_by(id=id).first()

    def remove(self, obj):
        try:
            db_session.delete(obj)
            db_session.commit()
            return obj
        except Exception:
            db_session.rollback()
            return 'fail'

    def save(self, obj):
        try:
            db_session.add(obj)
            db_session.commit()
            return obj
        except Exception:
            db_session.rollback()
            return 'fail'

    def update(self, obj):
        try:
            db_session.merge(obj)
            db_session.commit()
            return obj
        except Exception:
            db_session.rollback()
            return 'fail'

    def deleteAllNativeQuery(self):
        try:
            IndiceInvertido.query.delete()
            db_session.commit()
        except Exception:
            db_session.rollback()

    def inserirEntradaIndiceInvertido(self, termo, documento, f, peso):
        iv = IndiceInvertido()
        iv.documento = documento
        iv.documento_id = documento.id
        iv.frequencia = f
        iv.termo = termo
        iv.termo_id = termo.id
        iv.peso = peso
        self.save(iv)

    def getEntradasIndiceInvertido(self, termoConsulta):
        sql = ' select  i.* from TermoDocumento t, IndiceInvertido i, Documento d where t.id = i.termo_id and i.documento_id = d.id and t.texto = :termoConsulta '
        return db_session.query(IndiceInvertido).from_statement(text(sql)).params(termoConsulta=termoConsulta.texto).all()



class DocumentoService:

    def listAll(self):
        return Documento.query.all()

    def findById(self, ident):
        return Documento.query.filter_by(id=ident).first()

    def remove(self, obj):
        try:
            doclinks = DocumentoLink.query.filter_by(documento_id=obj.id).all()
            for doc in doclinks:
                db_session.delete(doc)
            indInv = IndiceInvertido.query.filter_by(documento_id=obj.id).all()
            for ind in indInv:
                db_session.delete(ind)
            db_session.delete(obj)
            db_session.commit()
            return obj
        except Exception:
            db_session.rollback()
            return 'fail'

    def save(self, obj):
        try:
            db_session.add(obj)
            db_session.commit()
            return obj
        except Exception:
            db_session.rollback()
            return 'fail'

    def update(self, obj):
        try:
            db_session.merge(obj)
            db_session.commit()
            return obj
        except Exception:
            db_session.rollback()
            return 'fail'

    def findByUrl(self, url):
        return Documento.query.filter_by(url=url).first()