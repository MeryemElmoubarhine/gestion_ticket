from django.contrib import admin
from .models import Ticket, Client, Historique, Profil

class TicketAdmin(admin.ModelAdmin):
    list_display = ('titre', 'client', 'statut', 'date_creation')
    list_filter = ('statut', 'client')
    search_fields = ('titre', 'description')

admin.site.register(Ticket, TicketAdmin)
admin.site.register(Client)
admin.site.register(Historique)
admin.site.register(Profil)
