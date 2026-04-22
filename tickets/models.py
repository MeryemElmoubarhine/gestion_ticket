from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

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

from django.db.models.signals import post_save
from django.dispatch import receiver

class Profil(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Administrateur'),
        ('technicien', 'Technicien'),
        ('utilisateur', 'Utilisateur'),
    ]
    utilisateur = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='utilisateur')

    def __str__(self):
        return f"{self.utilisateur.username} – {self.role}"

@receiver(post_save, sender=User)
def creer_profil(sender, instance, created, **kwargs):
    if created:
        Profil.objects.create(utilisateur=instance)
