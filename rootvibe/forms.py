from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, PermisConduire, DemandePlaque, Vehicule, Infraction, Photo,PaymentTransaction
from django.core.validators import RegexValidator
 
# -----------------------------------------------------------------------------
# Formulaire de création d'utilisateur personnalisé
# -----------------------------------------------------------------------------
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'telephone')
    
    # Les validateurs définis dans le modèle seront automatiquement utilisés.
    # Néanmoins, on peut ajouter des validations supplémentaires ici pour offrir
    # un retour immédiat à l'utilisateur.
    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if not first_name.replace(" ", "").replace("-", "").isalpha():
            raise forms.ValidationError("Le prénom ne doit contenir que des lettres, espaces ou tirets.")
        return first_name
    
    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if not last_name.replace(" ", "").replace("-", "").isalpha():
            raise forms.ValidationError("Le nom ne doit contenir que des lettres, espaces ou tirets.")
        return last_name

    def save(self, commit=True):
        user = super().save(commit=False)
        # Par défaut, le nouvel utilisateur est propriétaire.
        user.is_owner = True
        if commit:
            user.save()
        return user

# -----------------------------------------------------------------------------
# Formulaire pour le permis de conduire
# -----------------------------------------------------------------------------
class PermisConduireForm(forms.ModelForm):
    class Meta:
        model = PermisConduire
        fields = ['photo_identite']

# -----------------------------------------------------------------------------
# Formulaire pour la demande de plaque
# -----------------------------------------------------------------------------
class DemandePlaqueForm(forms.ModelForm):
    class Meta:
        model = DemandePlaque
        fields = ['vehicule']

    def __init__(self, *args, **kwargs):
        proprietaire = kwargs.pop('proprietaire', None)
        super().__init__(*args, **kwargs)
        if proprietaire:
            self.fields['vehicule'].queryset = Vehicule.objects.filter(proprietaire=proprietaire)

# -----------------------------------------------------------------------------
# Formulaire pour le véhicule
# -----------------------------------------------------------------------------
class VehiculeForm(forms.ModelForm):
    class Meta:
        model = Vehicule
        fields = ['marque', 'modele', 'couleur']

# -----------------------------------------------------------------------------
# Formulaire pour l'infraction
# -----------------------------------------------------------------------------
class InfractionForm(forms.ModelForm):
    class Meta:
        model = Infraction
        fields = ['type_infraction', 'date_infraction', 'montant_amende', 'lieu', 'preuve_photo']

# -----------------------------------------------------------------------------
# Formulaire pour la photo
# -----------------------------------------------------------------------------
class PhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ['image', 'type_photo']





class PaymentTransactionForm(forms.ModelForm):
    class Meta:
        model = PaymentTransaction
        # On laisse de côté merchant, payment_type, currency et callbackUrl qui sont définis par défaut
        fields = ['phone', 'reference', 'amount']
        widgets = {
            'phone': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Ex: +243818011389'
            }),
            'reference': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Entrez la référence du paiement'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Entrez le montant'
            }),
        }
