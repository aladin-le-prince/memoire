from django import template

register = template.Library()

@register.filter
def in_group(user, group_name):
    """
    Vérifie si l'utilisateur appartient au groupe dont le nom est group_name.
    Retourne True si l'utilisateur est authentifié et appartient au groupe,
    sinon retourne False.
    """
    if not user.is_authenticated:
        return False
    return user.groups.filter(name=group_name).exists()
