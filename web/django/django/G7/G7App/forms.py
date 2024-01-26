from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Aeroport
from .models import PistesAtterrissage
from .models import Compagnies
from .models import TypeAvions
from .models import Vols
from .models import Avions

class AeroportForm(forms.ModelForm):
    class Meta:
        model = Aeroport
        fields = ['nom', 'pays']

class PistesAtterrissageForm(forms.ModelForm):
    class Meta:
        model = PistesAtterrissage
        fields = ['numero','longueur', 'aeroport']
        widgets = {'aeroport': forms.Select(attrs={'class': 'form-select'}),}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['aeroport'].widget.choices = [(aeroport.id, aeroport.nom) for aeroport in Aeroport.objects.all()]

class CompagnieForm(forms.ModelForm):
    class Meta:
        model = Compagnies
        fields = ['nom', 'description', 'pays_rattachement']

class VolForm(forms.ModelForm):
    class Meta:
        model = Vols
        fields = ['avion', 
                  'pilote', 
                  'aeroport_depart', 
                  'piste_depart', 
                  'date_heure_depart', 
                  'aeroport_arrivee',
                  'piste_arrivee',
                  'date_heure_arrivee']
        widgets = {
            'avion': forms.Select(attrs={'class': 'form-select', 'id': 'id_avion'}),
            'pilote': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_pilote'}),
            'aeroport_depart': forms.Select(attrs={'class': 'form-select', 'id': 'id_aeroport_depart'}),
            'piste_depart': forms.Select(attrs={'class': 'form-select', 'id': 'id_piste_depart'}),
            'date_heure_depart': forms.DateTimeInput(attrs={'class': 'form-control', 'id': 'id_date_heure_depart'}),
            'aeroport_arrivee': forms.Select(attrs={'class': 'form-select', 'id': 'id_aeroport_arrivee'}),
            'piste_arrivee': forms.Select(attrs={'class': 'form-select', 'id': 'id_piste_arrivee'}),
            'date_heure_arrivee': forms.DateTimeInput(attrs={'class': 'form-control', 'id': 'id_date_heure_arrivee'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['avion'].widget.choices = [(avion.id, avion.nom) for avion in Avions.objects.all()]
        self.fields['aeroport_depart'].widget.choices = [(aeroport.id, aeroport.nom) for aeroport in Aeroport.objects.all()]
        self.fields['aeroport_arrivee'].widget.choices = [(aeroport.id, aeroport.nom) for aeroport in Aeroport.objects.all()]
        self.fields['piste_depart'].widget.choices = [(piste.id, piste.numero) for piste in PistesAtterrissage.objects.all()]
        self.fields['piste_arrivee'].widget.choices = [(piste.id, piste.numero) for piste in PistesAtterrissage.objects.all()]    

class TypeAvionForm(forms.ModelForm):
    class Meta:
        model = TypeAvions
        fields = ('marque', 'modele', 'description', 'images', 'longueur_piste_necessaire')

class AvionsForm(forms.ModelForm):
    class Meta:
        model = Avions
        fields = ('nom', 'compagnie', 'modele')
        widgets = {'compagnie': forms.Select(attrs={'class': 'form-select'}),}
        widgets = {'modele': forms.Select(attrs={'class': 'form-select'}),}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['compagnie'].widget.choices = [(compagnie.id, compagnie.nom) for compagnie in Compagnies.objects.all()]
        self.fields['modele'].widget.choices = [(type.id, type.modele) for type in TypeAvions.objects.all()]