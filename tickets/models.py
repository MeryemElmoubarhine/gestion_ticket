from django.contrib.auth.models import User
from django.db import models

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
        ('FERME', 'Fermé'),
    ]
    PRIORITE_CHOICES = [
        ('BASSE', 'Basse'),
        ('MOYENNE', 'Moyenne'),
        ('HAUTE', 'Haute'),
    ]

    titre = models.CharField(max_length=200)
    description = models.TextField()
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='OUVERT')
    priorite = models.CharField(max_length=10, choices=PRIORITE_CHOICES, default='MOYENNE')
    date_creation = models.DateTimeField(auto_now_add=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True, blank=True)
    technicien = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.titre

class Historique(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    utilisateur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.TextField()
    date_action = models.DateTimeField(auto_now_add=True)
