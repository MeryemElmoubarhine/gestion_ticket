from django.db import models
from django.contrib.auth.models import User
# Create your models here

class Client(models.Model):
    nom = models.CharField(max_length=100)
    email = models.EmailField()
    telephone = models.CharField(max_length=20)

    def __str__(self):
        return self.nom

class Ticket(models.Model):
    STATUT_CHOICES = [
        ('OUVERT', 'Ouvert'),
        ('EN_COURS', 'En cours'),
        ('RESOLU', 'Résolu'),
    ]

    titre = models.CharField(max_length=200)
    description = models.TextField()
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='OUVERT')
    date_creation = models.DateTimeField(auto_now_add=True)
    # Cette ligne crée le lien entre un ticket et un client
    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.titre

class Historique(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    utilisateur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.TextField()
    date_action = models.DateTimeField(auto_now_add=True)
