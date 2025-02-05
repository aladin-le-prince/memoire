
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import random
import string
class PermisConduire(models.Model):
    STATUT_CHOICES = [
        ('attente', 'En attente de validation'),
        ('valide', 'Valide'),
        ('suspendu', 'Suspendu')
    ]
    proprietaire = models.OneToOneField("rootvibe.Proprietaire", on_delete=models.CASCADE)
    numero_permis = models.CharField(max_length=15, unique=True)
    date_delivrance = models.DateField(auto_now_add=True)
    points = models.IntegerField(default=12)
    statut = models.CharField(choices=STATUT_CHOICES, max_length=10, default='attente')
    photo_identite = models.ImageField(upload_to='permis_photos/', blank=True, null=True)
    
    def verifier_suspension(self):
        if self.points <= 0:
            self.statut = 'suspendu'
            self.save()
    
    def __str__(self):
        return f"Permis {self.numero_permis} - {self.get_statut_display()}"




class Proprietaire(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    adresse = models.TextField()
    telephone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)

    SEXE_CHOICES = [
        ('M', 'Masculin'),
        ('F', 'Féminin'),
    ]
    sexe = models.CharField(choices=SEXE_CHOICES, max_length=1)

    def __str__(self):
        return f"{self.prenom} {self.nom}"

def generer_plaque_immatriculation():
    lettres_avant = ''.join(random.choices(string.ascii_uppercase, k=3))
    chiffres = ''.join(random.choices(string.digits, k=4))
    lettres_apres = ''.join(random.choices(string.ascii_uppercase, k=2))
    return f"{lettres_avant} {chiffres} {lettres_apres}"

class Vehicule(models.Model):
    proprietaire = models.ForeignKey(Proprietaire, on_delete=models.CASCADE)
    marque = models.CharField(max_length=100)
    modele = models.CharField(max_length=100)
    couleur = models.CharField(max_length=50)
    date_ajout = models.DateTimeField(default=timezone.now)
    plaque_immatriculation = models.CharField(max_length=20, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.plaque_immatriculation:
            self.plaque_immatriculation = generer_plaque_immatriculation()
            while Vehicule.objects.filter(plaque_immatriculation=self.plaque_immatriculation).exists():
                self.plaque_immatriculation = generer_plaque_immatriculation()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.plaque_immatriculation} - {self.marque} {self.modele}"

class DemandePlaque(models.Model):
    STATUT_CHOICES = [
        ('attente', 'En attente'),
        ('approuve', 'Approuvé'),
        ('rejete', 'Rejeté'),
    ]
    proprietaire = models.ForeignKey(Proprietaire, on_delete=models.CASCADE)
    vehicule = models.OneToOneField(Vehicule, on_delete=models.CASCADE)
    date_demande = models.DateField(auto_now_add=True)
    statut = models.CharField(choices=STATUT_CHOICES, max_length=10, default='attente')

    def approuver(self):
        """Attribuer une plaque et approuver la demande"""
        self.statut = 'approuve'
        self.vehicule.save()
        self.save()

    def __str__(self):
        return f"Demande {self.id} - {self.vehicule.marque} ({self.get_statut_display()})"

class Infraction(models.Model):
    vehicule = models.ForeignKey(Vehicule, on_delete=models.CASCADE)
    type_infraction = models.CharField(max_length=100)
    date_infraction = models.DateField()
    montant_amende = models.DecimalField(max_digits=10, decimal_places=2)
    lieu = models.TextField()

    def str(self):
        return f"{self.vehicule.plaque_immatriculation} - {self.type_infraction}"

# Choix pour le type de photo
class PhotoType(models.TextChoices):
    CARTE_IDENTITE = 'CI', 'Carte d\'identité'
    PLAQUE_IMMATRICULATION = 'PL', 'Plaque d\'immatriculation'

class Photo(models.Model):
    vehicule = models.ForeignKey(Vehicule, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='photos/')
    type_photo = models.CharField(max_length=2, choices=PhotoType.choices, default=PhotoType.PLAQUE_IMMATRICULATION)
    date_prise = models.DateField(auto_now_add=True)

    def str(self):
        return f"Photo de {self.get_type_photo_display()} pour {self.vehicule.plaque_immatriculation}"