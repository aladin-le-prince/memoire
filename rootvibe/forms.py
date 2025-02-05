from django import forms
from .models import User,DemandePlaque, Vehicule, Infraction, Photo,PermisConduire
from django.contrib.auth.forms import UserCreationForm


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        # Liste des champs que vous souhaitez proposer lors de l'inscription
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'telephone',
            'sexe',
        )


class VehiculeForm(forms.ModelForm):
    class Meta:
        model = Vehicule
        fields = ['plaque_immatriculation', 'marque', 'modele', 'couleur', 'proprietaire']

class InfractionForm(forms.ModelForm):
    class Meta:
        model = Infraction
        fields = ['vehicule', 'type_infraction', 'date_infraction', 'montant_amende', 'lieu']

class PhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ['vehicule', 'image', 'type_photo']
class PermisConduireForm(forms.ModelForm):
    class Meta:
        model = PermisConduire
        fields = ['photo_identite']
        

class DemandePlaqueForm(forms.ModelForm):
    class Meta:
        model = DemandePlaque
        fields = ['vehicule']
        widgets = {
            'vehicule': forms.Select(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        proprietaire = kwargs.pop('proprietaire', None)
        super().__init__(*args, **kwargs)
        if proprietaire:
            self.fields['vehicule'].queryset = Vehicule.objects.filter(proprietaire=proprietaire)
