from django.urls import path
from . import views

urlpatterns = [
    path('index/', views.index),

    # aeroports
    path('aeroport/ajouter/', views.ajouter_aeroport),
    path('aeroport/liste/', views.liste_aeroport),
    path('aeroport/supprimer/<int:id>/', views.supprimer_aeroport),
    path('aeroport/supprimer_confirm/<int:id>/', views.supprimer_confirm_aeroport),
    path('aeroport/modifier/<int:id>/', views.modifier_aeroport),
    
    path('aeroport/vols/<int:id>/',views.vols_aeroport),

    path('aeroport/ajouter_vols_depart/<int:id>/',views.ajouter_vols_depart_aeroport),
    path('aeroport/ajouter_vols_depart_traitement/<int:id>/', views.ajouter_vols_depart_traitement, name='ajouter_vols_depart_traitement'),
    path('aeroport/vols_depart/<int:id>/',views.vols_depart_aeroport),
    path('aeroport/ajouter_vols_arrivee/<int:id>/',views.ajouter_vols_arrivee_aeroport),
    path('aeroport/vols_arrivee/<int:id>/',views.vols_arrivee_aeroport),
    path('aeroport/ajouter_vols_depart_traitement/<int:id>/', views.ajouter_vols_depart_traitement, name='ajouter_vols_depart_traitement'),
    path('aeroport/ajouter_vols_arrivee_traitement/<int:id>/', views.ajouter_vols_arrivee_traitement, name='ajouter_vols_arrivee_traitement'),


    # pistes aeroports
    path('piste_aeroport/liste/', views.liste_piste),
    path('piste_aeroport/ajouter/', views.ajouter_piste),
    path('piste_aeroport/supprimer/<int:id>/', views.supprimer_piste),
    path('piste_aeroport/supprimer_confirm/<int:id>/', views.supprimer_confirm_piste),
    path('piste_aeroport/modifier/<int:id>/', views.modifier_piste),

    # Compagnie
    path('compagnie/liste/', views.liste_compagnie),
    path('compagnie/ajouter/', views.ajouter_compagnie),
    path('compagnie/supprimer/<int:id>/', views.supprimer_compagnie),
    path('compagnie/supprimer_confirm/<int:id>/', views.supprimer_confirm_compagnie),
    path('compagnie/modifier/<int:id>/', views.modifier_compagnie),

    # type avions
    path('type_avion/liste/', views.liste_typeavion),
    path('type_avion/ajouter/', views.ajouter_typeavion),
    path('type_avion/supprimer/<int:id>/', views.supprimer_typeavion),
    path('type_avion/supprimer_confirm/<int:id>/', views.supprimer_confirm_typeavion),
    path('type_avion/modifier/<int:id>/', views.modifier_typeavion),
    
    # vols
    path('vol/liste/', views.liste_vol),
    path('vol/ajouter/', views.ajouter_vol),
    path('vol/supprimer/<int:id>/', views.supprimer_vol),
    path('vol/supprimer_confirm/<int:id>/', views.supprimer_confirm_vol),
    path('vol/modifier/<int:id>/', views.modifier_vol),
    path('vol/pistes/<int:id>/', views.get_runways),

    #avion
    path('avion/liste/', views.liste_avion),
    path('avion/ajouter/', views.ajouter_avion),
    path('avion/supprimer/<int:id>/', views.supprimer_avion),
    path('avion/supprimer_confirm/<int:id>/', views.supprimer_confirm_avion),
    path('avion/modifier/<int:id>/', views.modifier_avion),
]
