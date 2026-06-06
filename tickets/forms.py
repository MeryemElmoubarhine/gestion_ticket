from django import forms
from .models import Ticket, Profil
from django.contrib.auth.models import User

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['titre', 'description', 'client', 'priorite', 'statut', 'technicien']
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'client': forms.Select(attrs={'class': 'form-select'}),
            'priorite': forms.Select(attrs={'class': 'form-select'}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
            'technicien': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Dropdown Technicien — uniquement les techniciens
        techniciens_ids = Profil.objects.filter(
            role='technicien'
        ).values_list('utilisateur_id', flat=True)
        self.fields['technicien'].queryset = User.objects.filter(
            id__in=techniciens_ids
        )

        # Dropdown Client — uniquement les utilisateurs
        clients_ids = Profil.objects.filter(
            role='utilisateur'
        ).values_list('utilisateur_id', flat=True)
        self.fields['client'].queryset = User.objects.filter(
            id__in=clients_ids
        )
