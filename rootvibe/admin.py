from django.contrib import admin
from .models import User, Vehicule, PermisConduire, DemandePlaque, Infraction, Photo

# Enregistrement des modèles pour qu'ils apparaissent dans l'admin
admin.site.register(User)
admin.site.register(Vehicule)
admin.site.register(PermisConduire)
admin.site.register(DemandePlaque)
admin.site.register(Infraction)
admin.site.register(Photo)

