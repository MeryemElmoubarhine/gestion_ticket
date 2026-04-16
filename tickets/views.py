from django.shortcuts import render

# Create your views here.
from .models import Ticket

def liste_tickets(request):
    # On récupère tous les tickets de la base de données
    tickets = Ticket.objects.all()
    return render(request, 'tickets/liste.html', {'tickets': tickets})
