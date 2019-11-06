from rest_framework.serializers import ModelSerializer
from .models import Documento


class ColetorSerializer(ModelSerializer):

    class Meta:
        model = Documento
        fields = ('__all__')

