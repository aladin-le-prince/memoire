from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import requests
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt  # 🚨 TEMPORAIRE : Désactive la protection CSRF pour tester
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


from .models import PermisConduire, User, DemandePlaque, Vehicule, Infraction, Photo,PaymentTransaction
from .forms import (
    VehiculeForm, InfractionForm, PhotoForm,
    PermisConduireForm, DemandePlaqueForm, PaymentTransactionForm ,CustomUserCreationForm
)

# ====================================================
# VUES GÉNÉRALES : Accueil, Connexion, Inscription, Déconnexion
# ====================================================

@login_required

def home(request):
    """
    Vue d'accueil qui redirige en fonction du rôle de l'utilisateur.
    """
    if request.user.is_authenticated:  #  Vérifier si l'utilisateur est connecté
        if request.user.is_owner:
            return redirect('owner_portal')
        elif request.user.is_agent:
            return redirect('search_vehicle')
        elif request.user.is_admin:
            return redirect('user_management')
        else:
            return redirect('default_dashboard')  #  Crée une page pour utilisateurs sans rôle
    return redirect('login')  #  Si non connecté, retour à la connexion

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)

            #  Sécurité : Vérifier si l'utilisateur est actif
            if not user.is_active:
                return render(request, 'auth/login.html', {'error': 'Compte désactivé'})

            #  Gestion des rôles
            if user.is_admin:
                return redirect('user_management')
            elif user.is_agent:
                return redirect('search_vehicle')
            elif user.is_owner:
                return redirect('owner_portal')
            else:
                return redirect('default_dashboard')  # ✅ Cas utilisateur sans rôle
            
        else:
            return render(request, 'auth/login.html', {'error': 'Identifiants invalides'})
    
    return render(request, 'auth/login.html')

def logout_view(request):
    logout(request)
    return redirect('home')

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            #  Vérifier que l'utilisateur a bien un rôle
            if not (user.is_owner or user.is_agent or user.is_admin):
                user.is_owner = True  #  Par défaut, on lui donne le rôle "propriétaire"
                user.save()

            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'auth/register.html', {'form': form})


# ====================================================
# VUES ADMIN
# ====================================================

@login_required
def user_management(request):
    users = User.objects.all()
    return render(request, 'admin/user_management.html', {'users': users})

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

@login_required
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    return redirect('user_management')

@login_required
def reports(request):
    total_vehicules = Vehicule.objects.count()
    total_infractions = Infraction.objects.count()
    return render(request, 'admin/reports.html', {
        'total_vehicules': total_vehicules,
        'total_infractions': total_infractions,
    })

# ====================================================
# VUES AGENT
# ====================================================

@login_required
def search_vehicle(request):
    if request.method == 'POST':
        plaque = request.POST.get('plaque', '')
        vehicules = Vehicule.objects.filter(plaque_immatriculation__icontains=plaque)
        return render(request, 'agent/search_vehicle.html', {'vehicules': vehicules})
    return render(request, 'agent/search_vehicle.html')

@login_required
def vehicle_details(request, vehicle_id):
    vehicule = get_object_or_404(Vehicule, id=vehicle_id)
    return render(request, 'agent/vehicle_details.html', {'vehicule': vehicule})

@login_required
def add_infraction(request, vehicle_id):
    vehicule = get_object_or_404(Vehicule, id=vehicle_id)
    if request.method == 'POST':
        form = InfractionForm(request.POST, request.FILES)
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
    return redirect('list_photos')

@login_required
def list_infractions(request):
    if request.user.is_staff or request.user.is_superuser:
        infractions = Infraction.objects.all()
    else:
        try:
            proprietaire = request.user
            infractions = Infraction.objects.filter(vehicule__proprietaire=proprietaire)
        except AttributeError:
            infractions = Infraction.objects.none()
    
    context = {
        'infractions': infractions,
        'vehicule': None,
    }
    return render(request, 'agent/list_infractions.html', context)

@login_required
def owner_infractions(request):
    try:
        proprietaire = request.user
        infractions = Infraction.objects.filter(vehicule__proprietaire=proprietaire)
    except AttributeError:
        infractions = Infraction.objects.none()

    context = {'infractions': infractions}
    return render(request, 'agent/list_infractions.html', context)

# ====================================================
# VUES PROPRIÉTAIRE
# ====================================================

@login_required
def owner_portal(request):
    vehicules = Vehicule.objects.filter(proprietaire=request.user)
    return render(request, 'owner/owner_portal.html', {'vehicules': vehicules})

@login_required
def owner_vehicle_details(request, vehicle_id):
    vehicule = get_object_or_404(Vehicule, id=vehicle_id, proprietaire=request.user)
    return render(request, 'owner/owner_vehicle_details.html', {'vehicule': vehicule})

@login_required
def add_vehicule(request):
    if request.method == 'POST':
        form = VehiculeForm(request.POST)
        if form.is_valid():
            vehicule = form.save(commit=False)
            vehicule.proprietaire = request.user  # Associe l'utilisateur connecté en tant que propriétaire
            vehicule.save()
            messages.success(request, 'Véhicule ajouté avec succès!')
            return redirect('owner_portal')
        else:
            messages.error(request, 'Erreur dans le formulaire.')
    else:
        form = VehiculeForm()
    return render(request, 'owner/add_vehicule.html', {'form': form})


# ====================================================
# VUES PERMIS
# ====================================================

@login_required
def demander_permis(request):
    proprietaire = request.user
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

# ====================================================
# VUES PLAQUES
# ====================================================

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

def statistiques_view(request):
    infraction_categories = Infraction.objects.values('nom').annotate(total=Count('id'))
    context = {
        'total_vehicules': Vehicule.objects.count(),
        'total_infractions': Infraction.objects.count(),
        'users': User.objects.filter(is_active=True),
        'infraction_categories': infraction_categories,
    }
    return render(request, 'statistiques.html', context)

def contact(request):
    return render(request, 'contact.html')

# ====================================================
# VUES PAIEMENT
# ====================================================
# Intégration de l'API Flexpay pour le traitement des paiements

def process_payment(
    merchant="TAJIRI",
    payment_type="1",
    phone="243973415646",
    reference="postman 1",
    amount="100",
    currency="CDF",
    callbackUrl="http://localhost"
):
    """
    Fonction utilitaire pour initier un paiement via l'API Flexpay.
    """
    url = "https://backend.flexpay.cd/api/rest/v1/paymentService"
    headers = {
        "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJcL2xvZ2luIiwicm9sZXMiOlsiTUVSQ0hBTlQiXSwiZXhwIjoxNzkyNDUyNzA5LCJzdWIiOiJkMzY1ZDdmMjU1NGY1ZDIzMGQ5ODA4MTgxMWE2NTE3YSJ9.y5uiKVPY0w8aexcaa6sB-UjKUDHRX9u8L1u04-JVzV0",
        "Content-Type": "application/json"
    }
    payload = {
        "merchant": merchant,
        "type": payment_type,
        "phone": phone,
        "reference": reference,
        "amount": amount,
        "currency": currency,
        "callbackUrl": callbackUrl
    }
    
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code in [200, 201]:
        return response.json()
    else:
        raise Exception(f"Échec du paiement : {response.status_code} {response.text}")

@require_http_methods(["GET", "POST"])
@login_required
def paiement_view(request):
    """
    Vue permettant à un utilisateur d'initier un paiement via l'API Flexpay.
    Utilise le formulaire PaymentTransactionForm pour collecter les données de paiement.
    Sur GET, affiche le template 'paiement.html'.
    Sur POST, valide le formulaire, appelle l'API, sauvegarde la transaction et affiche un template de succès.
    """
    if request.method == "POST":
        form = PaymentTransactionForm(request.POST)
        if form.is_valid():
            # Créer une instance sans sauvegarder immédiatement
            payment_transaction = form.save(commit=False)
            # Remplissage des champs par défaut
            payment_transaction.merchant = "TAJIRI"
            payment_transaction.payment_type = "1"
            payment_transaction.currency = "CDF"
            payment_transaction.callbackUrl = "http://localhost"  # À adapter en production
            
            # Générer une référence unique si nécessaire
            if not payment_transaction.reference:
                payment_transaction.reference = f"ref-{request.user.id}-{timezone.now().strftime('%Y%m%d%H%M%S')}"
            
            try:
                # Appel à l'API Flexpay
                payment_response = process_payment(
                    merchant=payment_transaction.merchant,
                    payment_type=payment_transaction.payment_type,
                    phone=payment_transaction.phone,
                    reference=payment_transaction.reference,
                    amount=str(payment_transaction.amount),
                    currency=payment_transaction.currency,
                    callbackUrl=payment_transaction.callbackUrl
                )
                # Mise à jour du statut de la transaction selon la réponse
                payment_transaction.status = 'success'
                payment_transaction.save()
                
                # Rediriger ou afficher une confirmation via un template dédié
                return render(request, 'paiement_success.html', {'payment_response': payment_response})
            except Exception as e:
                form.add_error(None, str(e))
    else:
        form = PaymentTransactionForm()
    
    return render(request, 'paiement.html', {'form': form})