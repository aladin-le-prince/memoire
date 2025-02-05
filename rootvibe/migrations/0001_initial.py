# Generated by Django 5.1.2 on 2025-02-05 03:22

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Proprietaire',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=100)),
                ('prenom', models.CharField(max_length=100)),
                ('adresse', models.TextField()),
                ('telephone', models.CharField(max_length=20)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('sex', models.CharField(choices=[('M ', 'masculin'), ('F ', 'feminin ')], max_length=10)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Vehicule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('plaque_immatriculation', models.CharField(max_length=20, unique=True)),
                ('marque', models.CharField(max_length=100)),
                ('modele', models.CharField(max_length=100)),
                ('couleur', models.CharField(max_length=50)),
                ('date_ajout', models.DateField(auto_now_add=True)),
                ('proprietaire', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rootvibe.proprietaire')),
            ],
        ),
        migrations.CreateModel(
            name='Photo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='photos/')),
                ('type_photo', models.CharField(choices=[('CI', "Carte d'identité"), ('PL', "Plaque d'immatriculation")], default='PL', max_length=2)),
                ('date_prise', models.DateField(auto_now_add=True)),
                ('vehicule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='photos', to='rootvibe.vehicule')),
            ],
        ),
        migrations.CreateModel(
            name='Infraction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type_infraction', models.CharField(max_length=100)),
                ('date_infraction', models.DateField()),
                ('montant_amende', models.DecimalField(decimal_places=2, max_digits=10)),
                ('lieu', models.TextField()),
                ('vehicule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rootvibe.vehicule')),
            ],
        ),
    ]
