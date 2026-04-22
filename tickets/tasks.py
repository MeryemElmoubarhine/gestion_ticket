from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta

@shared_task
def envoyer_email_nouveau_ticket(ticket_id):
    from .models import Ticket
    try:
        ticket = Ticket.objects.get(id=ticket_id)
        sujet = f"[EXPERTS ITN] Nouveau ticket #{ticket.id} - {ticket.titre}"
        message = f"""
Bonjour,

Un nouveau ticket a été créé :

Titre : {ticket.titre}
Description : {ticket.description}
Priorité : {ticket.get_priorite_display()}
Statut : {ticket.get_statut_display()}
Client : {ticket.client}

Merci de prendre en charge ce ticket.

Cordialement,
Système de Gestion des Tickets - EXPERTS ITN
"""
        if ticket.technicien and ticket.technicien.email:
            send_mail(sujet, message, 'noreply@experts-itn.com', [ticket.technicien.email])
            return f"Email envoyé au technicien {ticket.technicien.username}"
        return "Pas de technicien assigné"
    except Exception as e:
        return f"Erreur: {str(e)}"

@shared_task
def notifier_technicien(ticket_id):
    from .models import Ticket
    try:
        ticket = Ticket.objects.get(id=ticket_id)
        if ticket.technicien and ticket.technicien.email:
            sujet = f"[EXPERTS ITN] Ticket #{ticket.id} vous a été assigné"
            message = f"""
Bonjour {ticket.technicien.first_name},

Le ticket #{ticket.id} - "{ticket.titre}" vous a été assigné.

Priorité : {ticket.get_priorite_display()}
Client : {ticket.client}

Merci d'intervenir dès que possible.

Cordialement,
Système de Gestion des Tickets - EXPERTS ITN
"""
            send_mail(sujet, message, 'noreply@experts-itn.com', [ticket.technicien.email])
            return f"Notification envoyée à {ticket.technicien.username}"
        return "Pas de technicien assigné"
    except Exception as e:
        return f"Erreur: {str(e)}"

@shared_task
def fermer_tickets_inactifs():
    from .models import Ticket, Historique
    seuil = timezone.now() - timedelta(days=7)
    tickets = Ticket.objects.filter(
        statut='RESOLU',
        date_creation__lt=seuil
    )
    count = 0
    for ticket in tickets:
        ticket.statut = 'FERME'
        ticket.save()
        Historique.objects.create(
            ticket=ticket,
            action="Ticket fermé automatiquement (inactif depuis 7 jours)"
        )
        count += 1
    return f"{count} ticket(s) fermé(s) automatiquement"
