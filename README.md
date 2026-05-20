# 🎫 Gestion des Tickets IT — EXPERTS ITN

Application web de gestion des tickets IT développée dans le cadre du PFE.

## 👩‍💻 Développée par
Meryem Elmoubarhine — Stagiaire EXPERTS ITN

## 🛠️ Stack Technique
| Composant | Technologie |
|-----------|-------------|
| OS | AlmaLinux (VM VMware) |
| Backend | Django 6.0.4 (Python 3.12) |
| Base de données | PostgreSQL |
| Frontend | Bootstrap 5 + Chart.js |
| API | Django REST Framework |
| Automatisation | Celery + Redis |
| Serveur | Gunicorn + Nginx |

## 🚀 Installation

### 1. Cloner le projet
git clone https://github.com/MeryemElmoubarhine/gestion_ticket.git
cd gestion_ticket

### 2. Environnement virtuel
python3 -m venv mon_env
source mon_env/bin/activate
pip install -r requirements.txt

### 3. Configurer .env
Créer un fichier .env à la racine :
EMAIL_HOST_USER=votre.email@gmail.com
EMAIL_HOST_PASSWORD=votre_mot_de_passe_app

### 4. Base de données
python3 manage.py migrate
python3 manage.py createsuperuser

### 5. Lancer en développement
python3 manage.py runserver

### 6. Lancer en production
~/start_project.sh

## 👥 Rôles utilisateurs
| Rôle | Droits |
|------|--------|
| Admin | Tout faire |
| Technicien | Voir ses tickets, modifier |
| Utilisateur | Voir uniquement |

## 🔗 Endpoints API REST
| Méthode | URL | Description |
|---------|-----|-------------|
| GET | /api/tickets/ | Liste tous les tickets |
| GET | /api/tickets/<id>/ | Détail d'un ticket |
| POST | /api/tickets/creer/ | Créer un ticket |
| PUT | /api/tickets/<id>/modifier/ | Modifier un ticket |
| DELETE | /api/tickets/<id>/supprimer/ | Supprimer un ticket |
| GET | /api/stats/ | Statistiques globales |

## 📁 Structure du projet
gestion_ticket/
├── gestion_ticket/     # Configuration Django
├── tickets/            # App principale
│   ├── models.py       # Modèles de données
│   ├── views.py        # Vues web + API
│   ├── tasks.py        # Tâches Celery
│   └── templates/      # Templates HTML
├── requirements.txt
├── .env                # Non versionné
└── manage.py
