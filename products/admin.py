from django.contrib import admin
from .models import Product, Produit  # Ajout du modèle Produit


class ProductAdmin(admin.ModelAdmin):
    # Colonnes affichées dans la liste admin
    list_display = ['title', 'slug', 'brand', 'price', 'discount_price', 'timestamp', 'active', 'featured']
    
    # Champs pour la recherche
    search_fields = ['title', 'brand', 'slug', 'description']
    
    # Filtres latéraux pour un filtrage rapide
    list_filter = ['brand', 'active', 'featured', 'timestamp']
    
    # Champs préremplis (slug automatiquement basé sur le titre)
    prepopulated_fields = {'slug': ('title',)}
    
    # Pagination dans la liste
    list_per_page = 20


class ProduitAdmin(admin.ModelAdmin):
    list_display = ['nom', 'prix', 'date_ajout']
    search_fields = ['nom', 'description']
    list_filter = ['date_ajout']
    list_per_page = 20


# Enregistrement des modèles dans l'interface d'administration
admin.site.register(Product, ProductAdmin)
admin.site.register(Produit, ProduitAdmin)
