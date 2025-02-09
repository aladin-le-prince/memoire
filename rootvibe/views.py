from django.shortcuts import render
from rootvibe.utils import is_admin,is_admin, is_agent, is_proprietaire  
from django.shortcuts import render, redirect
 
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from .models import PermisConduire, User, DemandePlaque

from .models import Vehicule,  Infraction, Photo, PhotoType
from .forms import VehiculeForm, InfractionForm, PhotoForm
from django.contrib.auth.decorators import login_required

from .forms import PermisConduireForm,DemandePlaqueForm, CustomUserCreationForm


# Vue d'accueil
@login_required
def home(request):
    if request.user.is_owner:
        return redirect('owner_portal')
    elif request.user.is_agent:
        return redirect('search_vehicle')
    elif request.user.is_admin:
        return redirect('user_management')

# Connexion
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'auth/login.html', {'error': 'Identifiants invalides'})
    return render(request, 'auth/login.html')

# Déconnexion
def logout_view(request):
    logout(request)
    return redirect('home')

# Inscription (pour les propriétaires)
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')  # Rediriger vers la page de connexion ou autre
    else:
        form = CustomUserCreationForm()
    return render(request, 'auth/register.html', {'form': form})


# Gestion des utilisateurs (admin)
@login_required

def user_management(request):
    users = User.objects.all()
    return render(request, 'admin/user_management.html', {'users': users})

# Ajouter un utilisateur (admin)
@login_required

def add_user(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('user_management')
    else:
        form = CustomUserCreationForm()
    return render(request, 'admin/add_user.html', {'form': form})

# Modifier un utilisateur (admin)
@login_required

def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user_management')
    else:
        form = CustomUserCreationForm(instance=user)
    return render(request, 'admin/edit_user.html', {'form': form})

# Supprimer un utilisateur (admin)
@login_required

def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    return redirect('user_management')

# Rechercher un véhicule (agent)
@login_required

def search_vehicle(request):
    if request.method == 'POST':
        plaque = request.POST.get('plaque', '')
        vehicules = Vehicule.objects.filter(plaque_immatriculation__icontains=plaque)
        return render(request, 'agent/search_vehicle.html', {'vehicules': vehicules})
    return render(request, 'agent/search_vehicle.html')

# Détails d'un véhicule (agent)
@login_required

def vehicle_details(request, vehicle_id):
    vehicule = get_object_or_404(Vehicule, id=vehicle_id)
    return render(request, 'agent/vehicle_details.html', {'vehicule': vehicule})
# Ajouter une infraction (agent)
@login_required

def add_infraction(request, vehicle_id):
    vehicule = get_object_or_404(Vehicule, id=vehicle_id)
    if request.method == 'POST':
        form = InfractionForm(request.POST)
        if form.is_valid():
            infraction = form.save(commit=False)
            infraction.vehicule = vehicule
            infraction.save()
            return redirect('vehicle_details', vehicle_id=vehicle_id)
    else:
        form = InfractionForm()
    return render(request, 'agent/add_infraction.html', {'form': form, 'vehicule': vehicule})

def list_photos(request):
    photos = Photo.objects.all()
    return render(request, 'agent/list_photos.html', {'photos': photos})

# Ajouter une photo (agent)
@login_required

def add_photo(request, vehicle_id):
    vehicule = get_object_or_404(Vehicule, id=vehicle_id)
    if request.method == 'POST':
        form = PhotoForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.save(commit=False)
            photo.vehicule = vehicule
            photo.save()
            return redirect('vehicle_details', vehicle_id=vehicle_id)
    else:
        form = PhotoForm()
    return render(request, 'agent/add_photo.html', {'form': form, 'vehicule': vehicule})



def delete_photo(request, photo_id):
    photo = get_object_or_404(Photo, id=photo_id)
    photo.delete()
    return redirect('list_photos')  # Redirige vers la liste des photos après suppression

# Portail propriétaire
@login_required

def owner_portal(request):
    vehicules = Vehicule.objects.filter(proprietaire=request.user)
    return render(request, 'owner/owner_portal.html', {'vehicules': vehicules})

# Détails d'un véhicule (propriétaire)
@login_required

def owner_vehicle_details(request, vehicle_id):
    vehicule = get_object_or_404(Vehicule, id=vehicle_id, proprietaire=request.user)
    return render(request, 'owner/owner_vehicle_details.html', {'vehicule': vehicule})

# Statistiques et rapports (admin)
@login_required

def reports(request):
    # Exemple de statistiques
    total_vehicules = Vehicule.objects.count()
    total_infractions = Infraction.objects.count()
    return render(request, 'admin/reports.html', {
        'total_vehicules': total_vehicules,
        'total_infractions': total_infractions,
    })

# Page de contact
def contact(request):
    if request.method == 'POST':
        # Traiter le formulaire de contact (non implémenté ici)
        return redirect('home')
    return render(request, 'contact.html')


@login_required
def list_infractions(request):
    # Pour les administrateurs, afficher toutes les infractions
    if request.user.is_staff or request.user.is_superuser:
        infractions = Infraction.objects.all()
    else:
        # Pour un propriétaire, on suppose que l'utilisateur possède une relation vers User
        try:
            proprietaire = request.user
            # Filtrer les infractions liées aux véhicules appartenant à ce propriétaire
            infractions = Infraction.objects.filter(vehicule__proprietaire=proprietaire)
        except AttributeError:
            # Si l'utilisateur n'est pas associé à un objet User, retourner aucun résultat
            infractions = Infraction.objects.none()
    
    context = {
        'infractions': infractions,
        # Optionnel : si vous souhaitez afficher le véhicule sélectionné, vous pouvez l'ajouter ici
        'vehicule': None,
    }
    return render(request, 'agent/list_infractions.html', context)


@login_required
def owner_infractions(request):
    """
    Affiche les infractions liées aux véhicules du propriétaire connecté.
    """
    try:
        proprietaire = request.user
        infractions = Infraction.objects.filter(vehicule__proprietaire=proprietaire)
    except AttributeError:
        # Si l'utilisateur n'est pas associé à un objet User, on renvoie un queryset vide
        infractions = Infraction.objects.none()

    context = {
        'infractions': infractions,
    }
    # Vous pouvez réutiliser le même template que pour list_infractions ou en créer un spécifique
    return render(request, 'agent/list_infractions.html', context)

@login_required
def demander_permis(request):
    proprietaire = User.objects.get(user=request.user)
    if request.method == 'POST':
        form = PermisConduireForm(request.POST, request.FILES)
        if form.is_valid():
            permis = form.save(commit=False)
            permis.proprietaire = proprietaire
            permis.numero_permis = f"RDC-{proprietaire.id}"  # Génération simplifiée du numéro
            permis.save()
            return redirect('dashboard')
    else:
        form = PermisConduireForm()
    return render(request, 'permis/demande_permis.html', {'form': form})

@login_required
def valider_permis(request, permis_id):
    permis = PermisConduire.objects.get(id=permis_id)
    permis.statut = 'valide'
    permis.save()
    return redirect('admin_dashboard')

@login_required
def liste_permis(request):
    permis = PermisConduire.objects.all()
    return render(request, 'liste_permis.html', {'permis': permis})


@login_required
def demander_plaque(request):
    if request.method == "POST":
        form = DemandePlaqueForm(request.POST, proprietaire=request.user)
        if form.is_valid():
            demande = form.save(commit=False)
            demande.proprietaire = request.user
            demande.save()
            return redirect("liste_demandes")
    else:
        form = DemandePlaqueForm(proprietaire=request.user)

    return render(request, "plaque/demande_plaque.html", {"form": form})

def liste_demandes(request):
    demandes = DemandePlaque.objects.filter(statut="attente")
    return render(request, "plaque/liste_demandes.html", {"demandes": demandes})

@login_required
def approuver_demande(request, demande_id):
    demande = get_object_or_404(DemandePlaque, id=demande_id)
    demande.approuver()
    return redirect("liste_demandes")