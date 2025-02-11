from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator, EmailValidator
from django.utils import timezone
import random
import string

# -----------------------------------------------------------------------------
# Fonctions utilitaires
# -----------------------------------------------------------------------------
def generer_plaque_immatriculation():
    """
    Génère un numéro de plaque d'immatriculation selon un format standard
    (3 lettres, 4 chiffres, 2 lettres).
    """
    lettres_avant = ''.join(random.choices(string.ascii_uppercase, k=3))
    chiffres = ''.join(random.choices(string.digits, k=4))
    lettres_apres = ''.join(random.choices(string.ascii_uppercase, k=2))
    return f"{lettres_avant} {chiffres} {lettres_apres}"

# -----------------------------------------------------------------------------
# Validateurs personnalisés
# -----------------------------------------------------------------------------
# Valide le numéro de téléphone congolais.
phone_validator = RegexValidator(
    regex=r'^(?:\+243|0)[1-9]\d{7,8}$',
    message="Numéro de téléphone invalide. Le format doit être +243XXXXXXXX ou 0XXXXXXXX."
)

# Valide que le nom et le prénom ne contiennent que des lettres, espaces, apostrophes et tirets.
name_validator = RegexValidator(
    regex=r'^[A-Za-zÀ-ÖØ-öø-ÿ \'-]+$',
    message="Ce champ ne doit contenir que des lettres, espaces, apostrophes et tirets."
)

# -----------------------------------------------------------------------------
# Modèle Utilisateur Personnalisé
# -----------------------------------------------------------------------------
class User(AbstractUser):
    """
    Modèle utilisateur personnalisé avec trois rôles possibles.
    Par défaut, lors de l'inscription, un nouvel utilisateur est considéré comme propriétaire.
    """
    is_owner = models.BooleanField(default=True)
    is_agent = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    
    SEXE_CHOICES = [
        ('M', 'Masculin'),
        ('F', 'Féminin'),
    ]
    sexe = models.CharField(choices=SEXE_CHOICES, max_length=1, blank=True, null=True)
    
    # Validation pour le numéro de téléphone au format congolais.
    telephone = models.CharField(max_length=20, blank=True, null=True, validators=[phone_validator])
    
    # EmailField intègre déjà une validation, mais nous ajoutons un validateur explicite.
    email = models.EmailField(
        unique=True, 
        validators=[EmailValidator(message="Entrez une adresse email valide.")]
    )
    
    # Validation des noms avec des validateurs pour first_name et last_name.
    first_name = models.CharField(max_length=30, validators=[name_validator])
    last_name = models.CharField(max_length=30, validators=[name_validator])
    
    def __str__(self):
        role = 'Propriétaire' if self.is_owner else 'Agent' if self.is_agent else 'Admin' if self.is_admin else 'Utilisateur'
        return f"{self.first_name} {self.last_name} ({role})"
    
    def to_agent(self):
        self.is_owner = False
        self.is_admin = False
        self.is_agent = True
        self.save()

    def to_admin(self):
        self.is_owner = False
        self.is_agent = False
        self.is_admin = True
        self.save()

# -----------------------------------------------------------------------------
# Modèle Véhicule
# -----------------------------------------------------------------------------
class Vehicule(models.Model):
    proprietaire = models.ForeignKey(User, on_delete=models.CASCADE)
    marque = models.CharField(max_length=100)
    modele = models.CharField(max_length=100)
    couleur = models.CharField(max_length=50)
    date_ajout = models.DateTimeField(default=timezone.now)
    plaque_immatriculation = models.CharField(max_length=20, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.plaque_immatriculation:
            self.plaque_immatriculation = generer_plaque_immatriculation()
            # Assurer l'unicité de la plaque générée
            while Vehicule.objects.filter(plaque_immatriculation=self.plaque_immatriculation).exists():
                self.plaque_immatriculation = generer_plaque_immatriculation()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.plaque_immatriculation} - {self.marque} {self.modele}"

# -----------------------------------------------------------------------------
# Modèle Permis de Conduire
# -----------------------------------------------------------------------------
class PermisConduire(models.Model):
    STATUT_CHOICES = [
        ('attente', 'En attente de validation'),
        ('valide', 'Valide'),
        ('suspendu', 'Suspendu')
    ]
    # Le champ proprietaire fait référence à un utilisateur qui est propriétaire.
    proprietaire = models.OneToOneField(User, on_delete=models.CASCADE)
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

# -----------------------------------------------------------------------------
# Modèle Demande de Plaque
# -----------------------------------------------------------------------------
class DemandePlaque(models.Model):
    STATUT_CHOICES = [
        ('attente', 'En attente'),
        ('approuve', 'Approuvé'),
        ('rejete', 'Rejeté'),
    ]
    proprietaire = models.ForeignKey(User, on_delete=models.CASCADE)
    vehicule = models.OneToOneField(Vehicule, on_delete=models.CASCADE)
    date_demande = models.DateField(auto_now_add=True)
    statut = models.CharField(choices=STATUT_CHOICES, max_length=10, default='attente')

    def approuver(self):
        self.statut = 'approuve'
        self.vehicule.save()  # Possibilité d'automatiser des actions lors de l'approbation
        self.save()

    def __str__(self):
        return f"Demande {self.id} - {self.vehicule.marque} ({self.get_statut_display()})"

# -----------------------------------------------------------------------------
# Modèle Infraction
# -----------------------------------------------------------------------------
class Infraction(models.Model):
    vehicule = models.ForeignKey(Vehicule, on_delete=models.CASCADE)
    type_infraction = models.CharField(max_length=100)
    date_infraction = models.DateField()
    montant_amende = models.DecimalField(max_digits=10, decimal_places=2)
    lieu = models.TextField()
      # Nouveau champ pour la photo de preuve
    preuve_photo = models.ImageField(upload_to='infractions_preuves/', blank=True, null=True)
    def __str__(self):
        return f"{self.vehicule.plaque_immatriculation} - {self.type_infraction}"

# -----------------------------------------------------------------------------
# Modèle Photo et Type de Photo
# -----------------------------------------------------------------------------
class PhotoType(models.TextChoices):
    CARTE_IDENTITE = 'CI', "Carte d'identité"
    PLAQUE_IMMATRICULATION = 'PL', "Plaque d'immatriculation"

class Photo(models.Model):
    vehicule = models.ForeignKey(Vehicule, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='photos/')
    type_photo = models.CharField(max_length=2, choices=PhotoType.choices, default=PhotoType.PLAQUE_IMMATRICULATION)
    date_prise = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Photo de {self.get_type_photo_display()} pour {self.vehicule.plaque_immatriculation}"



class PaymentTransaction(models.Model):
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('success', 'Réussi'),
        ('failed', 'Échoué'),
    ]
    
    merchant = models.CharField(max_length=50, default="TAJIRI")
    payment_type = models.CharField(max_length=10, default="1")  # Type de paiement (par défaut "1")
    phone = models.CharField(
        max_length=20,
        validators=[RegexValidator(
            regex=r'^(?:\+243|0)[1-9]\d{7,8}$',
            message="Numéro de téléphone invalide. Le format doit être +243XXXXXXXX ou 0XXXXXXXX."
        )]
    )
    reference = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default="CDF")
    callbackUrl = models.URLField(default="http://localhost")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Paiement {self.reference} - {self.get_status_display()}"
