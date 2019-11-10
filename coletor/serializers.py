from rest_framework.serializers import ModelSerializer
from .models import Documento, Host, Link


class LinkSerializer(ModelSerializer):

    class Meta:
        model = Link
        fields = ('__all__')


class DocumentoSerializer(ModelSerializer):
    
    class Meta:
        model = Documento
        fields = ('__all__')

class HostSerializer(ModelSerializer):
    
    class Meta:
        model = Host
        fields = ('__all__')

