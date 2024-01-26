from django.db import models
from django.utils import timezone

class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)



class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class Aeroport(models.Model):
    id = models.SmallAutoField(primary_key=True)
    nom = models.CharField(max_length=40)
    pays = models.CharField(max_length=40)

    class Meta:
        managed = False
        db_table = 'aeroport'


class PistesAtterrissage(models.Model):
    id = models.SmallAutoField(primary_key=True)
    numero = models.IntegerField()
    longueur = models.SmallIntegerField()
    aeroport = models.ForeignKey(Aeroport, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.numero)

    class Meta:
        managed = False
        db_table = 'pistes_atterrissage'


class Compagnies(models.Model):
    id = models.SmallAutoField(primary_key=True)
    nom = models.CharField(max_length=40)
    description = models.CharField(max_length=200, blank=True, null=True)
    pays_rattachement = models.CharField(max_length=40)

    class Meta:
        managed = False
        db_table = 'compagnies'

def upload_to(instance, filename):
    timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
    return f'type_avions/{timestamp}_{filename}'

class TypeAvions(models.Model):
    id = models.SmallAutoField(primary_key=True)
    marque = models.CharField(max_length=40)
    modele = models.CharField(max_length=40)
    description = models.CharField(max_length=200, blank=True, null=True)
    images = models.ImageField(upload_to=upload_to, blank=True, null=True)
    longueur_piste_necessaire = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'type_avions'


class Avions(models.Model):
    id = models.SmallAutoField(primary_key=True)
    nom = models.CharField(max_length=40)
    compagnie = models.ForeignKey(Compagnies, on_delete=models.CASCADE)
    modele = models.ForeignKey(TypeAvions, on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'avions'


class Vols(models.Model):
    id = models.SmallAutoField(primary_key=True)
    avion = models.ForeignKey(Avions, on_delete=models.CASCADE)
    pilote = models.CharField(max_length=40)
    aeroport_depart = models.ForeignKey(Aeroport, on_delete=models.CASCADE, related_name='aeroport_depart')
    piste_depart = models.ForeignKey(PistesAtterrissage, on_delete=models.CASCADE, related_name='piste_depart')
    date_heure_depart = models.DateTimeField()
    aeroport_arrivee = models.ForeignKey(Aeroport, on_delete=models.CASCADE, related_name='aeroport_arrivee')
    piste_arrivee = models.ForeignKey(PistesAtterrissage, on_delete=models.CASCADE, related_name='piste_arrivee')
    date_heure_arrivee = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'vols'
