from .forms import AeroportForm, PistesAtterrissageForm, CompagnieForm, VolForm, TypeAvionForm, AvionsForm
from .models import Aeroport, PistesAtterrissage, Compagnies, Vols, TypeAvions, Avions
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import permission_required, login_required
import os
from django.conf import settings
from datetime import timedelta
from django.contrib import messages
import csv
from django.db import transaction
from datetime import datetime
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.http import HttpResponse
from django.http import JsonResponse
from django.db.models import Q

#import logging
#logger = logging.getLogger(__name__)

# Create your views here.
def index(request):
    return render(request, 'G7App/index.html')


# aeroport
def liste_aeroport(request):
    aeroports = Aeroport.objects.all()
    return render(request, 'G7App/aeroport/liste_aeroport.html', {'aeroports': aeroports})

# Only for prod
@login_required
@permission_required('Can add aeroport', raise_exception=True)
def ajouter_aeroport(request):
    if request.method == 'POST':
        form = AeroportForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'G7App/aeroport/confirmation_aeroport.html')
    else:
        form = AeroportForm()

    return render(request, 'G7App/aeroport/ajouter_aeroport.html',{'form': form})

# Only for prod
@login_required
@permission_required('Can change aeroport', raise_exception=True)
def modifier_aeroport(request, id):
    aeroport = Aeroport.objects.get(pk=id)
    form = AeroportForm(request.POST or None, instance=aeroport)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect("/G7App/aeroport/liste")
    return render(request, 'G7App/aeroport/modifier_aeroport.html', {'form': form, 'aeroport': aeroport})

# Only for prod
@login_required
@permission_required('Can delete aeroport', raise_exception=True)
def supprimer_aeroport(request, id):
    aeroport = Aeroport.objects.get(pk=id)
    return render(request, "G7App/aeroport/supprimer_aeroport.html", {"aeroport": aeroport})

# Only for prod
@login_required
@permission_required('Can delete aeroport', raise_exception=True)
def supprimer_confirm_aeroport(request, id):
    aeroport = Aeroport.objects.get(pk=id)
    aeroport.delete()
    return HttpResponseRedirect("/G7App/aeroport/liste/")

def vols_aeroport(request, id):
    aeroport = Aeroport.objects.get(pk=id)
    vols_depart = Vols.objects.filter(aeroport_depart=aeroport)
    vols_arrivee = Vols.objects.filter(aeroport_arrivee=aeroport)

    return render(request, 'G7App/aeroport/vols_aeroport.html', {'aeroport': aeroport,'vols_depart': vols_depart,'vols_arrivee':vols_arrivee})

# Only for prod
@login_required
@permission_required('Can add vol', raise_exception=True)
def ajouter_vols_depart_aeroport(request, id):
    aeroport = Aeroport.objects.get(pk=id)
    return render(request, 'G7App/aeroport/ajouter_vols_depart_aeroport.html', {'aeroport': aeroport})

# Only for prod
@login_required
@permission_required('Can add vol', raise_exception=True)
@transaction.atomic
def ajouter_vols_depart_traitement(request, id):
    aeroport = Aeroport.objects.get(pk=id)

    if request.method == 'POST' and request.FILES['csv_file']:
        csv_file = request.FILES['csv_file']
        if not csv_file.name.endswith('.csv'):
            # Handle error if the uploaded file is not a CSV file
            messages.error(request, "Le fichier n'est pas de type csv.")
            return HttpResponseRedirect(f"/G7App/aeroport/ajouter_vols_depart/{id}/")
        
        try:
            # Process the CSV file
            decoded_file = csv_file.read().decode('utf-8-sig')
            csv_data = csv.reader(decoded_file.splitlines(), delimiter=',')

            for row in csv_data:
                if len(row) != 7:
                    messages.error(request, "Le fichier CSV est mal formaté.")
                    return HttpResponseRedirect(f"/G7App/aeroport/ajouter_vols_depart/{id}/")
                    
                # Extract the data and create objects
                try:
                    avion_nom = row[0]
                    pilote = row[1]
                    piste_depart_numero = int(row[2])
                    date_heure_depart = datetime.strptime(row[3], "%Y-%m-%d %H:%M:%S")
                    aeroport_arrivee_nom = row[4]
                    piste_arrivee_nombre = int(row[5])
                    date_heure_arrivee = datetime.strptime(row[6], "%Y-%m-%d %H:%M:%S")

                    # Retrieve the airport and runway objects based on the names and numbers
                    avion = Avions.objects.get(nom=avion_nom)
                    aeroport_depart = Aeroport.objects.get(nom=aeroport.nom)
                    piste_depart = PistesAtterrissage.objects.get(numero=piste_depart_numero, aeroport=aeroport_depart)
                    aeroport_arrivee = Aeroport.objects.get(nom=aeroport_arrivee_nom)
                    piste_arrivee = PistesAtterrissage.objects.get(numero=piste_arrivee_nombre, aeroport=aeroport_arrivee)

                    # Create a new object and save it to the database
                    Vols.objects.create(avion=avion, pilote=pilote, aeroport_depart=aeroport_depart, piste_depart=piste_depart,
                                        date_heure_depart=date_heure_depart, aeroport_arrivee=aeroport_arrivee, 
                                        piste_arrivee=piste_arrivee, date_heure_arrivee=date_heure_arrivee)
                
                except (IndexError, ValueError) as e:
                    messages.error(request, f"Erreur de format dans le fichier CSV.")
                    return HttpResponseRedirect(f"/G7App/aeroport/ajouter_vols_depart/{id}/")
                
                except (Aeroport.DoesNotExist) as e:
                    messages.error(request, "L'aéroport spécifié n'existe pas.")
                    return HttpResponseRedirect(f"/G7App/aeroport/ajouter_vols_depart/{id}/")
                
                except (PistesAtterrissage.DoesNotExist) as e:
                    messages.error(request, "La piste spécifiée n'existe pas.")
                    return HttpResponseRedirect(f"/G7App/aeroport/ajouter_vols_depart/{id}/")
            
            # Redirect to a success page or display a success message
            return HttpResponseRedirect(f"/G7App/aeroport/vols/{id}/")
        
        except csv.Error as e:
            messages.error(request, "Erreur lors de la lecture du fichier CSV.")
            return HttpResponseRedirect(f"/G7App/aeroport/ajouter_vols_depart/{id}/")
            
    return render(request, 'G7App/aeroport/ajouter_vols_depart_aeroport.html', {'aeroport': aeroport})

def vols_depart_aeroport(request, id):
    aeroport = Aeroport.objects.get(pk=id)

    if request.method == 'POST':
        start_datetime = request.POST['start_datetime']
        end_datetime = request.POST['end_datetime']

        # Récupérer les vols associés à l'aéroport
        vols = Vols.objects.filter(
            Q(aeroport_depart=aeroport) &
            (
                (Q(date_heure_depart__lte=end_datetime) & Q(date_heure_depart__gte=start_datetime)) |
                (Q(date_heure_arrivee__lte=end_datetime) & Q(date_heure_arrivee__gte=start_datetime))
            )
        )

        # Charger le template contenant la structure du document PDF
        template = get_template('G7App/aeroport/fiche_vols_depart.html')

        # Contexte des données pour le template
        context = {'aeroport': aeroport, 'vols': vols}

        # Remplir le template avec les données
        rendered_template = template.render(context)

        # Créer un objet HttpResponse avec le contenu PDF
        pdf_file = HttpResponse(content_type='application/pdf')
        pdf_file['Content-Disposition'] = 'attachment; filename="fiche_vols_depart.pdf"'

        # Convertir le template HTML en PDF
        pisa_status = pisa.CreatePDF(rendered_template, dest=pdf_file)

        # Vérifier si la conversion en PDF s'est bien déroulée
        if pisa_status.err:
            return HttpResponse('Erreur lors de la génération du fichier PDF')

        return pdf_file
    else:
        return render(request, 'G7App/aeroport/vols_depart.html', {'aeroport': aeroport})

def vols_arrivee_aeroport(request, id):
    aeroport = Aeroport.objects.get(pk=id)

    if request.method == 'POST':
        start_datetime = request.POST['start_datetime']
        end_datetime = request.POST['end_datetime']

        # Récupérer les vols associés à l'aéroport
        vols = Vols.objects.filter(
            Q(aeroport_arrivee=aeroport) &
            (
                (Q(date_heure_depart__lte=end_datetime) & Q(date_heure_depart__gte=start_datetime)) |
                (Q(date_heure_arrivee__lte=end_datetime) & Q(date_heure_arrivee__gte=start_datetime))
            )
        )

        # Charger le template contenant la structure du document PDF
        template = get_template('G7App/aeroport/fiche_vols_arrivee.html')

        # Contexte des données pour le template
        context = {'aeroport': aeroport, 'vols': vols}

        # Remplir le template avec les données
        rendered_template = template.render(context)

        # Créer un objet HttpResponse avec le contenu PDF
        pdf_file = HttpResponse(content_type='application/pdf')
        pdf_file['Content-Disposition'] = 'attachment; filename="fiche_vols_arrivee.pdf"'

        # Convertir le template HTML en PDF
        pisa_status = pisa.CreatePDF(rendered_template, dest=pdf_file)

        # Vérifier si la conversion en PDF s'est bien déroulée
        if pisa_status.err:
            return HttpResponse('Erreur lors de la génération du fichier PDF')

        return pdf_file
    else:
        return render(request, 'G7App/aeroport/vols_arrivee.html', {'aeroport': aeroport})

# Only for prod
@login_required
@permission_required('Can add vol', raise_exception=True)
def ajouter_vols_arrivee_aeroport(request, id):
    aeroport = Aeroport.objects.get(pk=id)
    return render(request, 'G7App/aeroport/ajouter_vols_arrivee_aeroport.html', {'aeroport': aeroport})

# Only for prod
@login_required
@permission_required('Can add vol', raise_exception=True)
@transaction.atomic
def ajouter_vols_arrivee_traitement(request, id):
    aeroport = Aeroport.objects.get(pk=id)

    if request.method == 'POST' and request.FILES['csv_file']:
        csv_file = request.FILES['csv_file']
        if not csv_file.name.endswith('.csv'):
            # Handle error if the uploaded file is not a CSV file
            messages.error(request, "Le fichier n'est pas de type csv.")
            return HttpResponseRedirect(f"/G7App/aeroport/ajouter_vols_arrivee/{id}/")
        
        try:
            # Process the CSV file
            decoded_file = csv_file.read().decode('utf-8-sig')
            csv_data = csv.reader(decoded_file.splitlines(), delimiter=',')

            for row in csv_data:
                if len(row) != 7:
                    messages.error(request, "Le fichier CSV est mal formaté.")
                    return HttpResponseRedirect(f"/G7App/aeroport/ajouter_vols_arrivee/{id}/")
                    
                # Extract the data and create objects
                try:
                    avion_nom = row[0]
                    pilote = row[1]
                    aeroport_depart_nom = row[2]
                    piste_depart_numero = int(row[3])
                    date_heure_depart = datetime.strptime(row[4], "%Y-%m-%d %H:%M:%S")
                    piste_arrivee_nombre = int(row[5])
                    date_heure_arrivee = datetime.strptime(row[6], "%Y-%m-%d %H:%M:%S")

                    # Retrieve the airport and runway objects based on the names and numbers
                    avion = Avions.objects.get(nom=avion_nom)
                    aeroport_depart = Aeroport.objects.get(nom=aeroport_depart_nom)
                    piste_depart = PistesAtterrissage.objects.get(numero=piste_depart_numero, aeroport=aeroport_depart)
                    aeroport_arrivee = Aeroport.objects.get(nom=aeroport.nom)
                    piste_arrivee = PistesAtterrissage.objects.get(numero=piste_arrivee_nombre, aeroport=aeroport_arrivee)

                    # Create a new object and save it to the database
                    Vols.objects.create(avion=avion, pilote=pilote, aeroport_depart=aeroport_depart, piste_depart=piste_depart,
                                        date_heure_depart=date_heure_depart, aeroport_arrivee=aeroport_arrivee, 
                                        piste_arrivee=piste_arrivee, date_heure_arrivee=date_heure_arrivee)
                
                except (IndexError, ValueError) as e:
                    messages.error(request, f"Erreur de format dans le fichier CSV.")
                    return HttpResponseRedirect(f"/G7App/aeroport/ajouter_vols_arrivee/{id}/")
                
                except (Aeroport.DoesNotExist) as e:
                    messages.error(request, "L'aéroport spécifié n'existe pas.")
                    return HttpResponseRedirect(f"/G7App/aeroport/ajouter_vols_arrivee/{id}/")
                
                except (PistesAtterrissage.DoesNotExist) as e:
                    messages.error(request, "La piste spécifiée n'existe pas.")
                    return HttpResponseRedirect(f"/G7App/aeroport/ajouter_vols_arrivee/{id}/")
            
            # Redirect to a success page or display a success message
            return HttpResponseRedirect(f"/G7App/aeroport/vols/{id}/")
        
        except csv.Error as e:
            messages.error(request, "Erreur lors de la lecture du fichier CSV.")
            return HttpResponseRedirect(f"/G7App/aeroport/ajouter_vols_arrivee/{id}/")
            
    return render(request, 'G7App/aeroport/ajouter_vols_arrivee_aeroport.html', {'aeroport': aeroport})



# piste aeroport
def liste_piste(request):
    pistes = PistesAtterrissage.objects.all()
    return render(request, 'G7App/piste_aeroport/liste_piste.html', {'pistes': pistes})

# Only for prod
@login_required
@permission_required('Can add piste', raise_exception=True)
def ajouter_piste(request):
    aeroports = Aeroport.objects.all()
    if request.method == 'POST':
        form = PistesAtterrissageForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'G7App/piste_aeroport/confirmation_piste.html')
    else:
        form = PistesAtterrissageForm(initial={'aeroports': aeroports})
    return render(request, 'G7App/piste_aeroport/ajouter_piste.html',{'form': form, 'aeroports': aeroports})

# Only for prod
@login_required
@permission_required('Can change piste', raise_exception=True)
def modifier_piste(request, id):
    aeroports = Aeroport.objects.all()
    pistes = PistesAtterrissage.objects.get(pk=id)
    form = PistesAtterrissageForm(request.POST or None, instance=pistes)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect("/G7App/piste_aeroport/liste/")
    else:
        form = PistesAtterrissageForm(initial={'aeroports': aeroports})
    return render(request, 'G7App/piste_aeroport/modifier_piste.html', {'form': form, 'pistes': pistes, 'aeroports': aeroports})

# Only for prod
@login_required
@permission_required('Can delete piste', raise_exception=True)
def supprimer_piste(request, id):
    pistes = PistesAtterrissage.objects.get(pk=id)
    return render(request, "G7App/piste_aeroport/supprimer_piste.html", {"pistes": pistes})

# Only for prod
@login_required
@permission_required('Can delete piste', raise_exception=True)
def supprimer_confirm_piste(request, id):
    pistes = PistesAtterrissage.objects.get(pk=id)
    pistes.delete()
    return HttpResponseRedirect("/G7App/piste_aeroport/liste/")


# compagnie
def liste_compagnie(request):
    compagnies = Compagnies.objects.all()
    return render(request, 'G7App/compagnie/liste_compagnie.html', {'compagnies': compagnies})

# Only for prod
@login_required
@permission_required('Can add compagnie', raise_exception=True)
def ajouter_compagnie(request):
    if request.method == 'POST':
        form = CompagnieForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'G7App/compagnie/confirmation_compagnie.html')
    else:
        form = CompagnieForm()

    return render(request, 'G7App/compagnie/ajouter_compagnie.html',{'form': form})

# Only for prod
@login_required
@permission_required('Can change compagnie', raise_exception=True)
def modifier_compagnie(request, id):
    compagnies = Compagnies.objects.get(pk=id)
    form = CompagnieForm(request.POST or None, instance=compagnies)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect("/G7App/compagnie/liste")
    return render(request, 'G7App/compagnie/modifier_compagnie.html', {'form': form, 'compagnies': compagnies})

# Only for prod
@login_required
@permission_required('Can delete compagnie', raise_exception=True)
def supprimer_compagnie(request, id):
    compagnies = Compagnies.objects.get(pk=id)
    return render(request, "G7App/compagnie/supprimer_compagnie.html", {"compagnies": compagnies})

# Only for prod
@login_required
@permission_required('Can delete compagnie', raise_exception=True)
def supprimer_confirm_compagnie(request, id):
    compagnies = Compagnies.objects.get(pk=id)
    compagnies.delete()
    return HttpResponseRedirect("/G7App/compagnie/liste/")


# type avion
def liste_typeavion(request):
    types = TypeAvions.objects.all()
    return render(request, 'G7App/type_avion/liste_type_avion.html', {'types': types})

# Only for prod
@login_required
@permission_required('Can add typeavion', raise_exception=True)
def ajouter_typeavion(request):
    if request.method == 'POST':
        form = TypeAvionForm(request.POST,request.FILES)
        if form.is_valid():
            form.save()
            return render(request, 'G7App/type_avion/confirmation_type_avion.html')
    else:
        form = TypeAvionForm()

    return render(request, 'G7App/type_avion/ajouter_type_avion.html',{'form': form})

# Only for prod
@login_required
@permission_required('Can change typeavion', raise_exception=True)
def modifier_typeavion(request, id):
    types = TypeAvions.objects.get(pk=id)
    if request.method == 'POST':
        form = TypeAvionForm(request.POST or None,request.FILES or None, instance=types)
        if form.is_valid():
            if 'images' in form.changed_data and types.images:
                image_path = os.path.join(settings.MEDIA_ROOT, 'type_avions', types.images.name)

                if os.path.exists(image_path):
                    os.remove(image_path)

            form.save()
            return HttpResponseRedirect("/G7App/type_avion/liste/")
    else:
        form = TypeAvionForm(instance=types)
    
    return render(request, 'G7App/type_avion/modifier_type_avion.html', {'form': form, 'types': types})

# Only for prod
@login_required
@permission_required('Can delete typeavion', raise_exception=True)
def supprimer_typeavion(request, id):
    types = TypeAvions.objects.get(pk=id)
    return render(request, "G7App/type_avion/supprimer_type_avion.html", {"types": types})

# Only for prod
@login_required
@permission_required('Can delete typeavion', raise_exception=True)
def supprimer_confirm_typeavion(request, id):
    types = TypeAvions.objects.get(pk=id)
    types.delete()
    return HttpResponseRedirect("/G7App/type_avion/liste/")


# vol
def liste_vol(request):
    vols = Vols.objects.all()
    
    return render(request, 'G7App/vol/liste_vol.html', {'vols': vols})

# Only for prod
@login_required
@permission_required('Can add vol', raise_exception=True)
def ajouter_vol(request):
    if request.method == 'POST':
        form = VolForm(request.POST)
        
        if form.is_valid():
            vol = form.save(commit=False)

            # Vérifier la disponibilité des pistes
            date_heure_arrivee = vol.date_heure_arrivee
            aeroport_arrivee = vol.aeroport_arrivee
            piste_arrivee = vol.piste_arrivee
            
            date_heure_depart = vol.date_heure_depart
            aeroport_depart = vol.aeroport_depart
            piste_depart = vol.piste_depart
            
            vols_arrivee = Vols.objects.filter(
                ((Q(aeroport_arrivee=aeroport_arrivee, piste_arrivee=piste_arrivee) &
                Q(date_heure_arrivee__gte=date_heure_arrivee - timedelta(minutes=10)) &
                Q(date_heure_arrivee__lte=date_heure_arrivee)) |
                (Q(aeroport_depart=aeroport_arrivee, piste_depart=piste_arrivee) &
                Q(date_heure_depart__gte=date_heure_arrivee - timedelta(minutes=10)) &
                Q(date_heure_depart__lte=date_heure_arrivee))) |
                ((Q(aeroport_arrivee=aeroport_arrivee, piste_arrivee=piste_arrivee) &
                Q(date_heure_arrivee__gte=date_heure_arrivee) &
                Q(date_heure_arrivee__lte=date_heure_arrivee + timedelta(minutes=10))) |
                (Q(aeroport_depart=aeroport_arrivee, piste_depart=piste_arrivee) &
                Q(date_heure_depart__gte=date_heure_arrivee) &
                Q(date_heure_depart__lte=date_heure_arrivee + timedelta(minutes=10))))
            )

            vols_depart = Vols.objects.filter(
                ((Q(aeroport_depart=aeroport_depart, piste_depart=piste_depart) &
                Q(date_heure_depart__gte=date_heure_depart - timedelta(minutes=10)) &
                Q(date_heure_depart__lte=date_heure_depart)) |
                (Q(aeroport_arrivee=aeroport_depart, piste_arrivee=piste_depart) &
                Q(date_heure_arrivee__gte=date_heure_depart - timedelta(minutes=10)) &
                Q(date_heure_arrivee__lte=date_heure_depart))) |
                ((Q(aeroport_depart=aeroport_depart, piste_depart=piste_depart) &
                Q(date_heure_depart__gte=date_heure_depart) &
                Q(date_heure_depart__lte=date_heure_depart + timedelta(minutes=10))) |
                (Q(aeroport_arrivee=aeroport_depart, piste_arrivee=piste_depart) &
                Q(date_heure_arrivee__gte=date_heure_depart) &
                Q(date_heure_arrivee__lte=date_heure_depart + timedelta(minutes=10))))
            )
            
            piste_disponible_depart = None
            piste_disponible_arrivee = None

            if not (vols_arrivee.exists() or vols_depart.exists()):
                # Si aucun vol n'utilise ces pistes à l'heure d'arrivée/départ prévue le formulaire est bon
                form.save()
                return render(request, 'G7App/vol/confirmation_vol.html')
            
            else:
                data = request.POST.copy()
                
                if vols_arrivee.exists():
                    for piste in PistesAtterrissage.objects.filter(aeroport=aeroport_arrivee):
                        vols = Vols.objects.filter(
                            ((Q(aeroport_arrivee=aeroport_arrivee, piste_arrivee=piste) &
                            Q(date_heure_arrivee__gte=date_heure_arrivee - timedelta(minutes=10)) &
                            Q(date_heure_arrivee__lte=date_heure_arrivee)) |
                            (Q(aeroport_depart=aeroport_arrivee, piste_depart=piste) &
                            Q(date_heure_depart__gte=date_heure_arrivee - timedelta(minutes=10)) &
                            Q(date_heure_depart__lte=date_heure_arrivee))) |
                            ((Q(aeroport_arrivee=aeroport_arrivee, piste_arrivee=piste) &
                            Q(date_heure_arrivee__gte=date_heure_arrivee) &
                            Q(date_heure_arrivee__lte=date_heure_arrivee + timedelta(minutes=10))) |
                            (Q(aeroport_depart=aeroport_arrivee, piste_depart=piste) &
                            Q(date_heure_depart__gte=date_heure_arrivee) &
                            Q(date_heure_depart__lte=date_heure_arrivee + timedelta(minutes=10))))
                        )

                        if not vols.exists():
                            # Si aucun vol n'utilise cette piste à l'heure d'arrivée prévue, la piste est disponible
                            piste_disponible_arrivee = piste
                            # Cannot prefill the data as javascript overwrites it (deactivated)
                            data["piste_arrivee"] = piste
                            messages.error(request, f"La piste n`est pas disponible à l`heure d`arrivée. La piste {piste.__str__()} est disponible (ajouter manuellement).")
                            
                            form.data = data
                            break
                
                if vols_depart.exists():      
                    for piste in PistesAtterrissage.objects.filter(aeroport=aeroport_depart):
                        vols = Vols.objects.filter(
                            ((Q(aeroport_depart=aeroport_depart, piste_depart=piste) &
                            Q(date_heure_depart__gte=date_heure_depart - timedelta(minutes=10)) &
                            Q(date_heure_depart__lte=date_heure_depart)) |
                            (Q(aeroport_arrivee=aeroport_depart, piste_arrivee=piste) &
                            Q(date_heure_arrivee__gte=date_heure_depart - timedelta(minutes=10)) &
                            Q(date_heure_arrivee__lte=date_heure_depart))) |
                            ((Q(aeroport_depart=aeroport_depart, piste_depart=piste) &
                            Q(date_heure_depart__gte=date_heure_depart) &
                            Q(date_heure_depart__lte=date_heure_depart + timedelta(minutes=10))) |
                            (Q(aeroport_arrivee=aeroport_depart, piste_arrivee=piste) &
                            Q(date_heure_arrivee__gte=date_heure_depart) &
                            Q(date_heure_arrivee__lte=date_heure_depart + timedelta(minutes=10))))
                        )
                        
                        if not vols.exists():
                            # Si aucun vol n'utilise cette piste à l'heure de départ prévue, la piste est disponible
                            piste_disponible_depart = piste
                            # Cannot prefill the data as javascript overwrites it (deactivated)
                            data["piste_depart"] = piste
                            messages.error(request, f"La piste n`est pas disponible à l`heure de départ. La piste {piste.__str__()} est disponible (ajouter manuellement).")
                            
                            form.data = data
                            break

                if piste_disponible_arrivee is None and vols_arrivee.exists():
                    # Si aucune piste n'est disponible, proposer un nouvel horaire
                    dernier_vol = Vols.objects.filter(
                        Q(aeroport_arrivee=aeroport_arrivee, piste_arrivee=piste_arrivee,
                        date_heure_arrivee__gte=date_heure_arrivee) |
                        Q(aeroport_depart=aeroport_arrivee, piste_depart=piste_arrivee,
                        date_heure_depart__gte=date_heure_arrivee)
                        ).order_by("date_heure_arrivee", "date_heure_depart").first()

                    nouvel_horaire = dernier_vol.date_heure_arrivee + timedelta(minutes=10) + timedelta(seconds=1)
                    nouvelle_piste = dernier_vol.piste_arrivee
                    messages.error(request, f"Aucune piste n`est disponible à l`heure d`arrivée. Veuillez choisir un horaire ultérieur. Le prochain horaire disponible est {nouvel_horaire} sur la piste {nouvelle_piste.__str__()}.")
                            
                    data["date_heure_arrivee"] = nouvel_horaire
                    data["piste_arrivee"] = nouvelle_piste
                    form.data = data
                
                if piste_disponible_depart is None and vols_depart.exists():
                    # Si aucune piste n'est disponible, proposer un nouvel horaire

                    dernier_vol = Vols.objects.filter(
                        Q(aeroport_depart=aeroport_depart, piste_depart=piste_depart,
                        date_heure_depart__gte=date_heure_depart) |
                        Q(aeroport_arrivee=aeroport_depart, piste_arrivee=piste_depart,
                        date_heure_arrivee__gte=date_heure_depart)
                        ).order_by("date_heure_depart", "date_heure_arrivee").first()

                    nouvel_horaire = dernier_vol.date_heure_depart + timedelta(minutes=10) + timedelta(seconds=1)
                    nouvelle_piste = dernier_vol.piste_depart
                    messages.error(request, f"Aucune piste n`est disponible à l`heure de départ. Veuillez choisir un horaire ultérieur. Le prochain horaire disponible est {nouvel_horaire} sur la piste {nouvelle_piste.__str__()}.")
                            
                    data["date_heure_depart"] = nouvel_horaire
                    data["piste_depart"] = nouvelle_piste
                    form.data = data
            
    else:
        form = VolForm()

    return render(request, 'G7App/vol/ajouter_vol.html',{'form': form})

@login_required
@permission_required('Can add vol', raise_exception=True)
def get_runways(request, id):
    # Filter the runways based on the selected airport
    runways = PistesAtterrissage.objects.filter(aeroport_id=id).values('id', 'numero')
    return JsonResponse(list(runways), safe=False)

# Only for prod
@login_required
@permission_required('Can change vol', raise_exception=True)
def modifier_vol(request, id):
    vol = Vols.objects.get(pk=id)
    form = VolForm(request.POST or None, instance=vol)
    
    if form.is_valid():
        vol = form.save(commit=False)

        # Vérifier la disponibilité des pistes
        date_heure_arrivee = vol.date_heure_arrivee
        aeroport_arrivee = vol.aeroport_arrivee
        piste_arrivee = vol.piste_arrivee
        
        date_heure_depart = vol.date_heure_depart
        aeroport_depart = vol.aeroport_depart
        piste_depart = vol.piste_depart
        
        vols_arrivee = Vols.objects.filter(
            ((Q(aeroport_arrivee=aeroport_arrivee, piste_arrivee=piste_arrivee) &
            Q(date_heure_arrivee__gte=date_heure_arrivee - timedelta(minutes=10)) &
            Q(date_heure_arrivee__lte=date_heure_arrivee)) |
            (Q(aeroport_depart=aeroport_arrivee, piste_depart=piste_arrivee) &
            Q(date_heure_depart__gte=date_heure_arrivee - timedelta(minutes=10)) &
            Q(date_heure_depart__lte=date_heure_arrivee))) |
            ((Q(aeroport_arrivee=aeroport_arrivee, piste_arrivee=piste_arrivee) &
            Q(date_heure_arrivee__gte=date_heure_arrivee) &
            Q(date_heure_arrivee__lte=date_heure_arrivee + timedelta(minutes=10))) |
            (Q(aeroport_depart=aeroport_arrivee, piste_depart=piste_arrivee) &
            Q(date_heure_depart__gte=date_heure_arrivee) &
            Q(date_heure_depart__lte=date_heure_arrivee + timedelta(minutes=10))))
        )

        vols_depart = Vols.objects.filter(
            ((Q(aeroport_depart=aeroport_depart, piste_depart=piste_depart) &
            Q(date_heure_depart__gte=date_heure_depart - timedelta(minutes=10)) &
            Q(date_heure_depart__lte=date_heure_depart)) |
            (Q(aeroport_arrivee=aeroport_depart, piste_arrivee=piste_depart) &
            Q(date_heure_arrivee__gte=date_heure_depart - timedelta(minutes=10)) &
            Q(date_heure_arrivee__lte=date_heure_depart))) |
            ((Q(aeroport_depart=aeroport_depart, piste_depart=piste_depart) &
            Q(date_heure_depart__gte=date_heure_depart) &
            Q(date_heure_depart__lte=date_heure_depart + timedelta(minutes=10))) |
            (Q(aeroport_arrivee=aeroport_depart, piste_arrivee=piste_depart) &
            Q(date_heure_arrivee__gte=date_heure_depart) &
            Q(date_heure_arrivee__lte=date_heure_depart + timedelta(minutes=10))))
        )

        piste_disponible_depart = None
        piste_disponible_arrivee = None
        test = False
        
        # pour ne pas reprendre lui-même
        
        if not (vols_arrivee.exists() or vols_depart.exists()) or (vol in vols_arrivee and vol in vols_depart):
            # Si aucun vol n'utilise ces pistes à l'heure d'arrivée/départ prévue le formulaire est bon
            form.save()
            return HttpResponseRedirect("/G7App/vol/liste")
        
        else:
            data = request.POST.copy()
            
            if vols_arrivee.exists() and not vol in vols_arrivee:
                for piste in PistesAtterrissage.objects.filter(aeroport=aeroport_arrivee):
                    vols = Vols.objects.filter(
                        ((Q(aeroport_arrivee=aeroport_arrivee, piste_arrivee=piste) &
                        Q(date_heure_arrivee__gte=date_heure_arrivee - timedelta(minutes=10)) &
                        Q(date_heure_arrivee__lte=date_heure_arrivee)) |
                        (Q(aeroport_depart=aeroport_arrivee, piste_depart=piste) &
                        Q(date_heure_depart__gte=date_heure_arrivee - timedelta(minutes=10)) &
                        Q(date_heure_depart__lte=date_heure_arrivee))) |
                        ((Q(aeroport_arrivee=aeroport_arrivee, piste_arrivee=piste) &
                        Q(date_heure_arrivee__gte=date_heure_arrivee) &
                        Q(date_heure_arrivee__lte=date_heure_arrivee + timedelta(minutes=10))) |
                        (Q(aeroport_depart=aeroport_arrivee, piste_depart=piste) &
                        Q(date_heure_depart__gte=date_heure_arrivee) &
                        Q(date_heure_depart__lte=date_heure_arrivee + timedelta(minutes=10))))
                    )

                    if not vols.exists():
                        # Si aucun vol n'utilise cette piste à l'heure d'arrivée prévue, la piste est disponible
                        piste_disponible_arrivee = piste
                        # Cannot prefill the data as javascript overwrites it (deactivated)
                        data["piste_arrivee"] = piste
                        messages.error(request, f"La piste n`est pas disponible à l`heure d`arrivée. La piste {piste.__str__()} est disponible (ajouter manuellement).")
                        
                        form.data = data
                        test = True
                        break
               
            if vols_depart.exists() and not vol in vols_depart:      
                for piste in PistesAtterrissage.objects.filter(aeroport=aeroport_depart):
                    vols = Vols.objects.filter(
                        ((Q(aeroport_depart=aeroport_depart, piste_depart=piste) &
                        Q(date_heure_depart__gte=date_heure_depart - timedelta(minutes=10)) &
                        Q(date_heure_depart__lte=date_heure_depart)) |
                        (Q(aeroport_arrivee=aeroport_depart, piste_arrivee=piste) &
                        Q(date_heure_arrivee__gte=date_heure_depart - timedelta(minutes=10)) &
                        Q(date_heure_arrivee__lte=date_heure_depart))) |
                        ((Q(aeroport_depart=aeroport_depart, piste_depart=piste) &
                        Q(date_heure_depart__gte=date_heure_depart) &
                        Q(date_heure_depart__lte=date_heure_depart + timedelta(minutes=10))) |
                        (Q(aeroport_arrivee=aeroport_depart, piste_arrivee=piste) &
                        Q(date_heure_arrivee__gte=date_heure_depart) &
                        Q(date_heure_arrivee__lte=date_heure_depart + timedelta(minutes=10))))
                    )
                    
                    if not vols.exists():
                        # Si aucun vol n'utilise cette piste à l'heure de départ prévue, la piste est disponible
                        piste_disponible_depart = piste
                        # Cannot prefill the data as javascript overwrites it (deactivated)
                        data["piste_depart"] = piste
                        messages.error(request, f"La piste n`est pas disponible à l`heure de départ. La piste {piste.__str__()} est disponible (ajouter manuellement).")
                        
                        form.data = data
                        test = True
                        break

            if piste_disponible_arrivee is None and vols_arrivee.exists() and not vol in vols_arrivee:
                # Si aucune piste n'est disponible, proposer un nouvel horaire
                dernier_vol = Vols.objects.filter(
                    Q(aeroport_arrivee=aeroport_arrivee, piste_arrivee=piste_arrivee,
                    date_heure_arrivee__gte=date_heure_arrivee) |
                    Q(aeroport_depart=aeroport_arrivee, piste_depart=piste_arrivee,
                    date_heure_depart__gte=date_heure_arrivee)
                    ).order_by("date_heure_arrivee", "date_heure_depart").first()

                nouvel_horaire = dernier_vol.date_heure_arrivee + timedelta(minutes=10) + timedelta(seconds=1)
                nouvelle_piste = dernier_vol.piste_arrivee
                messages.error(request, f"Aucune piste n`est disponible à l`heure d`arrivée. Veuillez choisir un horaire ultérieur. Le prochain horaire disponible est {nouvel_horaire} sur la piste {nouvelle_piste.__str__()}.")
                        
                data["date_heure_arrivee"] = nouvel_horaire
                data["piste_arrivee"] = nouvelle_piste
                form.data = data
                test = True
            
            if piste_disponible_depart is None and vols_depart.exists() and not vol in vols_depart:
                # Si aucune piste n'est disponible, proposer un nouvel horaire

                dernier_vol = Vols.objects.filter(
                    Q(aeroport_depart=aeroport_depart, piste_depart=piste_depart,
                    date_heure_depart__gte=date_heure_depart) |
                    Q(aeroport_arrivee=aeroport_depart, piste_arrivee=piste_depart,
                    date_heure_arrivee__gte=date_heure_depart)
                    ).order_by("date_heure_depart", "date_heure_arrivee").first()

                nouvel_horaire = dernier_vol.date_heure_depart + timedelta(minutes=10) + timedelta(seconds=1)
                nouvelle_piste = dernier_vol.piste_depart
                messages.error(request, f"Aucune piste n`est disponible à l`heure de départ. Veuillez choisir un horaire ultérieur. Le prochain horaire disponible est {nouvel_horaire} sur la piste {nouvelle_piste.__str__()}.")
                        
                data["date_heure_depart"] = nouvel_horaire
                data["piste_depart"] = nouvelle_piste
                form.data = data
                test = True
        
        if not test:
            form.save()
            return HttpResponseRedirect("/G7App/vol/liste")
    
    return render(request, 'G7App/vol/modifier_vol.html', {'form': form, 'vol': vol})

# Only for prod
@login_required
@permission_required('Can delete vol', raise_exception=True)
def supprimer_vol(request, id):
    vol = Vols.objects.get(pk=id)
    
    return render(request, "G7App/vol/supprimer_vol.html", {"vol": vol})

# Only for prod
@login_required
@permission_required('Can delete vol', raise_exception=True)
def supprimer_confirm_vol(request, id):
    vol = Vols.objects.get(pk=id)
    vol.delete()
    
    return HttpResponseRedirect("/G7App/vol/liste/")


# type avion
def liste_avion(request):
    avions = Avions.objects.all()
    return render(request, 'G7App/avion/liste_avion.html', {'avions': avions})

# Only for prod
@login_required
@permission_required('Can add piste', raise_exception=True)
def ajouter_avion(request):
    compagnies = Compagnies.objects.all()
    modeles = TypeAvions.objects.all()
    if request.method == 'POST':
        form = AvionsForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'G7App/avion/confirmation_avion.html')
    else:
        form = AvionsForm(initial={'compagnies':compagnies,'modeles': modeles})
    return render(request, 'G7App/avion/ajouter_avion.html',{'form': form, 'compagnies': compagnies, 'modeles' : modeles})

# Only for prod
@login_required
@permission_required('Can change piste', raise_exception=True)
def modifier_avion(request, id):
    avions = Avions.objects.get(pk=id)
    form = AvionsForm(request.POST or None, instance=avions)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect("/G7App/avion/liste/")
    
    return render(request, 'G7App/avion/modifier_avion.html', {'form': form, 'avions' : avions})

# Only for prod
@login_required
@permission_required('Can delete piste', raise_exception=True)
def supprimer_avion(request, id):
    avions = Avions.objects.get(pk=id)
    return render(request, "G7App/avion/supprimer_avion.html", {"avions": avions})

# Only for prod
@login_required
@permission_required('Can delete piste', raise_exception=True)
def supprimer_confirm_avion(request, id):
    avions = Avions.objects.get(pk=id)
    avions.delete()
    return HttpResponseRedirect("/G7App/avion/liste/")