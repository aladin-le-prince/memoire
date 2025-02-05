# myapp/context_processors.py

def user_groups(request):
    """
    Retourne des variables indiquant si l'utilisateur connecté
    appartient aux groupes "Agent" ou "Proprietaire".
    """
    user = request.user
    return {
        'is_agent': user.is_authenticated and user.groups.filter(name="Agent").exists(),
        'is_proprietaire': user.is_authenticated and user.groups.filter(name="Proprietaire").exists(),
    }
