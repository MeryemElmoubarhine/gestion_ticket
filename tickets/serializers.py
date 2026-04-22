from rest_framework import serializers
from .models import Ticket, Client, Historique
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'

class HistoriqueSerializer(serializers.ModelSerializer):
    utilisateur = UserSerializer(read_only=True)
    class Meta:
        model = Historique
        fields = '__all__'

class TicketSerializer(serializers.ModelSerializer):
    client_nom = serializers.CharField(source='client.nom', read_only=True)
    technicien_nom = serializers.CharField(source='technicien.username', read_only=True)
    historique = HistoriqueSerializer(many=True, read_only=True)

    class Meta:
        model = Ticket
        fields = [
            'id', 'titre', 'description',
            'statut', 'priorite', 'date_creation',
            'client', 'client_nom',
            'technicien', 'technicien_nom',
            'historique'
        ]
