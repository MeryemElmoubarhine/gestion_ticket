from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Ticket, Historique, Profil
from .forms import TicketForm
from django.contrib.auth.models import User
from .tasks import envoyer_email_nouveau_ticket, notifier_technicien

def get_role(user):
    try:
        return user.profil.role
    except:
        return 'utilisateur'

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
    role = get_role(request.user)

    if role == 'admin' or request.user.is_superuser:
        return redirect('dashboard_admin')
    elif role == 'technicien':
        return redirect('dashboard_technicien')
    else:
        return redirect('dashboard_utilisateur')

# ── DASHBOARD ADMIN ──────────────────────────────────────
@login_required(login_url='login')
def dashboard_admin(request):
    role = get_role(request.user)
    if role != 'admin' and not request.user.is_superuser:
        return redirect('dashboard')

    total    = Ticket.objects.count()
    ouverts  = Ticket.objects.filter(statut='OUVERT').count()
    resolus  = Ticket.objects.filter(statut='RESOLU').count()
    en_cours = Ticket.objects.filter(statut='EN_COURS').count()
    fermes   = Ticket.objects.filter(statut='FERME').count()
    haute    = Ticket.objects.filter(priorite='HAUTE').count()
    moyenne  = Ticket.objects.filter(priorite='MOYENNE').count()
    basse    = Ticket.objects.filter(priorite='BASSE').count()
    techniciens = User.objects.filter(profil__role='technicien')
    utilisateurs = User.objects.filter(profil__role='utilisateur')
    derniers_tickets = Ticket.objects.all().order_by('-date_creation')[:5]

    return render(request, 'tickets/dashboard_admin.html', {
        'total': total, 'ouverts': ouverts, 'resolus': resolus,
        'en_cours': en_cours, 'fermes': fermes,
        'haute': haute, 'moyenne': moyenne, 'basse': basse,
        'techniciens': techniciens, 'utilisateurs': utilisateurs,
        'derniers_tickets': derniers_tickets,
        'nb_techniciens': techniciens.count(),
        'nb_utilisateurs': utilisateurs.count(),
    })

# ── DASHBOARD TECHNICIEN ─────────────────────────────────
@login_required(login_url='login')
def dashboard_technicien(request):
    role = get_role(request.user)
    if role != 'technicien':
        return redirect('dashboard')

    mes_tickets = Ticket.objects.filter(technicien=request.user)
    total       = mes_tickets.count()
    ouverts     = mes_tickets.filter(statut='OUVERT').count()
    en_cours    = mes_tickets.filter(statut='EN_COURS').count()
    resolus     = mes_tickets.filter(statut='RESOLU').count()
    fermes      = mes_tickets.filter(statut='FERME').count()
    haute       = mes_tickets.filter(priorite='HAUTE').count()
    derniers    = mes_tickets.order_by('-date_creation')[:5]

    return render(request, 'tickets/dashboard_technicien.html', {
        'total': total, 'ouverts': ouverts,
        'en_cours': en_cours, 'resolus': resolus,
        'fermes': fermes, 'haute': haute,
        'derniers_tickets': derniers,
    })

# ── DASHBOARD UTILISATEUR ────────────────────────────────
@login_required(login_url='login')
def dashboard_utilisateur(request):
    role = get_role(request.user)
    if role != 'utilisateur':
        return redirect('dashboard')

    tous_tickets = Ticket.objects.all()
    total    = tous_tickets.count()
    ouverts  = tous_tickets.filter(statut='OUVERT').count()
    resolus  = tous_tickets.filter(statut='RESOLU').count()
    en_cours = tous_tickets.filter(statut='EN_COURS').count()
    derniers = tous_tickets.order_by('-date_creation')[:5]

    return render(request, 'tickets/dashboard_utilisateur.html', {
        'total': total, 'ouverts': ouverts,
        'resolus': resolus, 'en_cours': en_cours,
        'derniers_tickets': derniers,
    })

# ── GESTION UTILISATEURS (admin seulement) ───────────────
@login_required(login_url='login')
def gestion_utilisateurs(request):
    role = get_role(request.user)
    if role != 'admin' and not request.user.is_superuser:
        messages.error(request, "Accès refusé.")
        return redirect('dashboard')
    users = User.objects.all().select_related('profil')
    return render(request, 'tickets/gestion_utilisateurs.html', {'users': users})

@login_required(login_url='login')
def changer_role(request, user_id):
    role = get_role(request.user)
    if role != 'admin' and not request.user.is_superuser:
        return redirect('dashboard')
    if request.method == 'POST':
        user = get_object_or_404(User, pk=user_id)
        nouveau_role = request.POST.get('role')
        profil, _ = Profil.objects.get_or_create(utilisateur=user)
        profil.role = nouveau_role
        profil.save()
        messages.success(request, f"Rôle de {user.username} changé en {nouveau_role}")
    return redirect('gestion_utilisateurs')

# ── TICKETS ──────────────────────────────────────────────
@login_required(login_url='login')
def liste_tickets(request):
    role = get_role(request.user)
    if role == 'technicien':
        tickets = Ticket.objects.filter(technicien=request.user).order_by('-date_creation')
    else:
        tickets = Ticket.objects.all().order_by('-date_creation')
    return render(request, 'tickets/liste.html', {'tickets': tickets, 'role': role})

@login_required(login_url='login')
def creer_ticket(request):
    form = TicketForm()
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save()
            Historique.objects.create(ticket=ticket, utilisateur=request.user, action="Ticket créé")
            envoyer_email_nouveau_ticket.delay(ticket.id)
            notifier_technicien.delay(ticket.id)
            messages.success(request, "Ticket créé avec succès !")
            return redirect('liste_tickets')
    return render(request, 'tickets/creer_ticket.html', {'form': form})

@login_required(login_url='login')
def detail_ticket(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    historique = Historique.objects.filter(ticket=ticket).order_by('-date_action')
    role = get_role(request.user)
    return render(request, 'tickets/detail_ticket.html', {
        'ticket': ticket, 'historique': historique, 'role': role,
    })

@login_required(login_url='login')
def modifier_ticket(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    role = get_role(request.user)
    if role == 'utilisateur':
        messages.error(request, "Permission refusée.")
        return redirect('liste_tickets')
    form = TicketForm(instance=ticket)
    if request.method == 'POST':
        form = TicketForm(request.POST, instance=ticket)
        if form.is_valid():
            form.save()
            Historique.objects.create(ticket=ticket, utilisateur=request.user, action=f"Ticket modifié par {request.user.username}")
            messages.success(request, "Ticket modifié avec succès !")
            return redirect('liste_tickets')
    return render(request, 'tickets/modifier_ticket.html', {'form': form, 'ticket': ticket})

@login_required(login_url='login')
def supprimer_ticket(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    role = get_role(request.user)
    if role != 'admin' and not request.user.is_superuser:
        messages.error(request, "Seul un admin peut supprimer.")
        return redirect('liste_tickets')
    if request.method == 'POST':
        ticket.delete()
        messages.success(request, "Ticket supprimé.")
        return redirect('liste_tickets')
    return render(request, 'tickets/supprimer_ticket.html', {'ticket': ticket})

# ── API REST ─────────────────────────────────────────────
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import TicketSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_tickets_list(request):
    tickets = Ticket.objects.all().order_by('-date_creation')
    serializer = TicketSerializer(tickets, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_ticket_detail(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    serializer = TicketSerializer(ticket)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_creer_ticket(request):
    serializer = TicketSerializer(data=request.data)
    if serializer.is_valid():
        ticket = serializer.save()
        Historique.objects.create(ticket=ticket, utilisateur=request.user, action="Ticket créé via API")
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def api_modifier_ticket(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    serializer = TicketSerializer(ticket, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def api_supprimer_ticket(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    ticket.delete()
    return Response({'message': 'Ticket supprimé'}, status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_stats(request):
    return Response({
        'total': Ticket.objects.count(),
        'ouverts': Ticket.objects.filter(statut='OUVERT').count(),
        'en_cours': Ticket.objects.filter(statut='EN_COURS').count(),
        'resolus': Ticket.objects.filter(statut='RESOLU').count(),
        'fermes': Ticket.objects.filter(statut='FERME').count(),
        'haute': Ticket.objects.filter(priorite='HAUTE').count(),
        'moyenne': Ticket.objects.filter(priorite='MOYENNE').count(),
        'basse': Ticket.objects.filter(priorite='BASSE').count(),
    })
