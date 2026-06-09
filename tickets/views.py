from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import TicketSerializer
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Ticket, Historique, Profil
from .forms import TicketForm
from django.contrib.auth.models import User
import json

try:
    from .tasks import envoyer_email_nouveau_ticket, notifier_technicien
except ImportError:
    envoyer_email_nouveau_ticket = None
    notifier_technicien = None


# ─── UTILITAIRE RÔLE ────────────────────────────────────────────────────────

def get_role(user):
    try:
        return user.profil.role
    except:
        return 'utilisateur'


# ─── AUTHENTIFICATION ────────────────────────────────────────────────────────

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
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


# ─── DASHBOARD ───────────────────────────────────────────────────────────────

@login_required(login_url='login')
def dashboard(request):
    role = get_role(request.user)
    if role == 'admin' or request.user.is_superuser:
        return redirect('dashboard_admin')
    elif role == 'technicien':
        return redirect('dashboard_technicien')
    else:
        return redirect('dashboard_utilisateur')


@login_required(login_url='login')
def dashboard_admin(request):
    role = get_role(request.user)
    if role != 'admin' and not request.user.is_superuser:
        return redirect('dashboard')

    tickets = Ticket.objects.all()
    total = tickets.count()
    ouverts = tickets.filter(statut='OUVERT').count()
    en_cours = tickets.filter(statut='EN_COURS').count()
    resolus = tickets.filter(statut='RESOLU').count()
    fermes = tickets.filter(statut='FERME').count()
    haute = tickets.filter(priorite='HAUTE').count()
    moyenne = tickets.filter(priorite='MOYENNE').count()
    basse = tickets.filter(priorite='BASSE').count()
    nb_techniciens = User.objects.filter(profil__role='technicien').count()
    nb_utilisateurs = User.objects.filter(profil__role='utilisateur').count()
    derniers_tickets = tickets.order_by('-date_creation')[:5]

    return render(request, 'tickets/dashboard_admin.html', {
        'total': total,
        'ouverts': ouverts,
        'en_cours': en_cours,
        'resolus': resolus,
        'fermes': fermes,
        'haute': haute,
        'moyenne': moyenne,
        'basse': basse,
        'nb_techniciens': nb_techniciens,
        'nb_utilisateurs': nb_utilisateurs,
        'derniers_tickets': derniers_tickets,
    })


@login_required(login_url='login')
def dashboard_technicien(request):
    role = get_role(request.user)
    if role != 'technicien':
        return redirect('dashboard')

    tickets = Ticket.objects.filter(technicien=request.user)
    mes_ouverts = tickets.filter(statut='OUVERT').count()
    mes_en_cours = tickets.filter(statut='EN_COURS').count()
    mes_resolus = tickets.filter(statut='RESOLU').count()
    mes_fermes = tickets.filter(statut='FERME').count()
    urgents = tickets.filter(priorite='HAUTE').count()
    a_traiter = tickets.filter(statut='OUVERT').count()
    derniers_tickets = tickets.order_by('-date_creation')[:5]

    return render(request, 'tickets/dashboard_technicien.html', {
        'mes_tickets': tickets.count(),
        'a_traiter': a_traiter,
        'mes_en_cours': mes_en_cours,
        'urgents': urgents,
        'mes_ouverts': mes_ouverts,
        'mes_resolus': mes_resolus,
        'mes_fermes': mes_fermes,
        'derniers_tickets': derniers_tickets,
    })


@login_required(login_url='login')
def dashboard_utilisateur(request):
    role = get_role(request.user)
    if role != 'utilisateur':
        return redirect('dashboard')

    derniers_tickets = Ticket.objects.filter(client=request.user).order_by('-date_creation')
    total = derniers_tickets.count()
    ouverts = derniers_tickets.filter(statut='OUVERT').count()
    resolus = derniers_tickets.filter(statut='RESOLU').count()

    return render(request, 'tickets/dashboard_utilisateur.html', {
        'derniers_tickets': derniers_tickets,
        'total': total,
        'ouverts': ouverts,
        'resolus': resolus,
    })


# ─── TICKETS ─────────────────────────────────────────────────────────────────

@login_required(login_url='login')
def liste_tickets(request):
    role = get_role(request.user)
    if role == 'technicien':
        tickets = Ticket.objects.filter(technicien=request.user).order_by('-date_creation')
    elif role == 'utilisateur':
        tickets = Ticket.objects.filter(client=request.user).order_by('-date_creation')
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
            Historique.objects.create(
                ticket=ticket,
                utilisateur=request.user,
                action="Ticket créé"
            )
            if envoyer_email_nouveau_ticket:
                envoyer_email_nouveau_ticket.delay(ticket.id)
            if notifier_technicien:
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
        'ticket': ticket,
        'historique': historique,
        'role': role,
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
            Historique.objects.create(
                ticket=ticket,
                utilisateur=request.user,
                action=f"Ticket modifié par {request.user.username}"
            )
            messages.success(request, "Ticket modifié avec succès !")
            return redirect('liste_tickets')
    return render(request, 'tickets/modifier_ticket.html', {'form': form, 'ticket': ticket})


@login_required(login_url='login')
def supprimer_ticket(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    role = get_role(request.user)
    if role != 'admin' and not request.user.is_superuser:
        messages.error(request, "Seul un administrateur peut supprimer un ticket.")
        return redirect('liste_tickets')
    if request.method == 'POST':
        ticket.delete()
        messages.success(request, "Ticket supprimé avec succès.")
        return redirect('liste_tickets')
    return render(request, 'tickets/supprimer_ticket.html', {'ticket': ticket})


# ─── GESTION UTILISATEURS ────────────────────────────────────────────────────

@login_required(login_url='login')
def gestion_utilisateurs(request):
    role = get_role(request.user)
    if role != 'admin' and not request.user.is_superuser:
        messages.error(request, "Accès refusé.")
        return redirect('dashboard')
    users = User.objects.all().select_related('profil').order_by('username')
    return render(request, 'tickets/gestion_utilisateurs.html', {'users': users})


@login_required(login_url='login')
def changer_role(request, user_id):
    role = get_role(request.user)
    if role != 'admin' and not request.user.is_superuser:
        messages.error(request, "Accès refusé.")
        return redirect('dashboard')
    if request.method == 'POST':
        user = get_object_or_404(User, pk=user_id)
        nouveau_role = request.POST.get('role')
        if nouveau_role in ['admin', 'technicien', 'utilisateur']:
            profil, _ = Profil.objects.get_or_create(utilisateur=user)
            profil.role = nouveau_role
            profil.save()
            messages.success(request, f"Rôle de {user.username} changé en {nouveau_role}.")
        else:
            messages.error(request, "Rôle invalide.")
    return redirect('gestion_utilisateurs')


# ─── API REST ─────────────────────────────────────────────────────────────────

@login_required(login_url='login')
def api_tickets_list(request):
    tickets = Ticket.objects.all().order_by('-date_creation')
    data = []
    for t in tickets:
        data.append({
            'id': t.id,
            'titre': t.titre,
            'description': t.description,
            'statut': t.statut,
            'priorite': t.priorite,
            'date_creation': t.date_creation.isoformat(),
            'client': t.client.username if t.client else None,
            'technicien': t.technicien.username if t.technicien else None,
        })
    return JsonResponse(data, safe=False)


@login_required(login_url='login')
def api_ticket_detail(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    historique = list(Historique.objects.filter(ticket=ticket).order_by('-date_action').values(
        'id', 'action', 'date_action', 'utilisateur__username'
    ))
    data = {
        'id': ticket.id,
        'titre': ticket.titre,
        'description': ticket.description,
        'statut': ticket.statut,
        'priorite': ticket.priorite,
        'date_creation': ticket.date_creation.isoformat(),
        'client': ticket.client.username if ticket.client else None,
        'technicien': ticket.technicien.username if ticket.technicien else None,
        'historique': historique,
    }
    return JsonResponse(data)


@csrf_exempt
@login_required(login_url='login')
def api_creer_ticket(request):
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            ticket = Ticket.objects.create(
                titre=body.get('titre', ''),
                description=body.get('description', ''),
                statut=body.get('statut', 'OUVERT'),
                priorite=body.get('priorite', 'MOYENNE'),
            )
            Historique.objects.create(
                ticket=ticket,
                utilisateur=request.user,
                action="Ticket créé via API"
            )
            return JsonResponse({'id': ticket.id, 'message': 'Ticket créé avec succès'}, status=201)
        except Exception as e:
            return JsonResponse({'erreur': str(e)}, status=400)
    return JsonResponse({'erreur': 'Méthode non autorisée'}, status=405)


@csrf_exempt
@login_required(login_url='login')
def api_modifier_ticket(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    if request.method == 'PUT':
        try:
            body = json.loads(request.body)
            ticket.titre = body.get('titre', ticket.titre)
            ticket.description = body.get('description', ticket.description)
            ticket.statut = body.get('statut', ticket.statut)
            ticket.priorite = body.get('priorite', ticket.priorite)
            ticket.save()
            Historique.objects.create(
                ticket=ticket,
                utilisateur=request.user,
                action=f"Ticket modifié via API par {request.user.username}"
            )
            return JsonResponse({'message': 'Ticket modifié avec succès'})
        except Exception as e:
            return JsonResponse({'erreur': str(e)}, status=400)
    return JsonResponse({'erreur': 'Méthode non autorisée'}, status=405)


@csrf_exempt
@login_required(login_url='login')
def api_supprimer_ticket(request, pk):
    role = get_role(request.user)
    if role != 'admin' and not request.user.is_superuser:
        return JsonResponse({'erreur': 'Permission refusée'}, status=403)
    ticket = get_object_or_404(Ticket, pk=pk)
    if request.method == 'DELETE':
        ticket.delete()
        return JsonResponse({'message': 'Ticket supprimé avec succès'})
    return JsonResponse({'erreur': 'Méthode non autorisée'}, status=405)


@login_required(login_url='login')
def api_stats(request):
    tickets = Ticket.objects.all()
    data = {
        'total': tickets.count(),
        'ouverts': tickets.filter(statut='OUVERT').count(),
        'en_cours': tickets.filter(statut='EN_COURS').count(),
        'resolus': tickets.filter(statut='RESOLU').count(),
        'fermes': tickets.filter(statut='FERME').count(),
        'haute': tickets.filter(priorite='HAUTE').count(),
        'moyenne': tickets.filter(priorite='MOYENNE').count(),
        'basse': tickets.filter(priorite='BASSE').count(),
        'nb_techniciens': User.objects.filter(profil__role='technicien').count(),
        'nb_utilisateurs': User.objects.filter(profil__role='utilisateur').count(),
    }
    return JsonResponse(data)


def accueil(request):
    return render(request, 'tickets/accueil.html')
