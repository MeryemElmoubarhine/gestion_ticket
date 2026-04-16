from django.contrib import admin

# Register your models here.
from .models import Ticket, Client

class TicketAdmin(admin.ModelAdmin):
    # Liste des colonnes à afficher dans l'interface
    list_display = ('titre', 'client', 'statut', 'date_creation')
    # Ajouter un filtre sur le côté pour le statut
    list_filter = ('statut', 'client')
    # Ajouter une barre de recherche
    search_fields = ('titre', 'description')
admin.site.register(Ticket, TicketAdmin)
admin.site.register(Client)
