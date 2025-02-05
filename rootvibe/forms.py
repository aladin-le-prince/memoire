from django import forms
from .models import Proprietaire,DemandePlaque, Vehicule, Infraction, Photo,PermisConduire
from django.contrib.auth.models import User


class ProprietaireForm(forms.ModelForm):
    class Meta:
        model = Proprietaire
        fields = '__all__'  


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

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
