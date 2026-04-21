from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Ticket, Historique
from .forms import TicketForm

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
    return render(request, 'tickets/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
def dashboard(request):
    total    = Ticket.objects.count()
    ouverts  = Ticket.objects.filter(statut='OUVERT').count()
    resolus  = Ticket.objects.filter(statut='RESOLU').count()
    en_cours = Ticket.objects.filter(statut='EN_COURS').count()
    return render(request, 'tickets/dashboard.html', {
        'total': total,
        'ouverts': ouverts,
        'resolus': resolus,
        'urgents': en_cours,
    })

@login_required(login_url='login')
def liste_tickets(request):
    tickets = Ticket.objects.all().order_by('-date_creation')
    return render(request, 'tickets/liste.html', {'tickets': tickets})

@login_required(login_url='login')
def creer_ticket(request):
    form = TicketForm()
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save()
            Historique.objects.create(
                ticket=ticket,
                utilisateur=request.user,
                action="Ticket créé"
            )
            messages.success(request, "Ticket créé avec succès !")
            return redirect('liste_tickets')
    return render(request, 'tickets/creer_ticket.html', {'form': form})

@login_required(login_url='login')
def detail_ticket(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    historique = Historique.objects.filter(ticket=ticket).order_by('-date_action')
    return render(request, 'tickets/detail_ticket.html', {
        'ticket': ticket,
        'historique': historique
    })

@login_required(login_url='login')
def modifier_ticket(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    form = TicketForm(instance=ticket)
    if request.method == 'POST':
        form = TicketForm(request.POST, instance=ticket)
        if form.is_valid():
            form.save()
            Historique.objects.create(
                ticket=ticket,
                utilisateur=request.user,
                action="Ticket modifié"
            )
            messages.success(request, "Ticket modifié avec succès !")
            return redirect('liste_tickets')
    return render(request, 'tickets/modifier_ticket.html', {'form': form, 'ticket': ticket})

@login_required(login_url='login')
def supprimer_ticket(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    if request.method == 'POST':
        ticket.delete()
        messages.success(request, "Ticket supprimé.")
        return redirect('liste_tickets')
    return render(request, 'tickets/supprimer_ticket.html', {'ticket': ticket})
