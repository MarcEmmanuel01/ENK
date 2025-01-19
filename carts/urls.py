from django.urls import path
from . import views

urlpatterns = [
    # Vue principale du panier
    path('', views.cart_home, name='cart'),

    # Ajouter un produit au panier
    path('add/', views.add_to_cart, name='add_to_cart'),

    # Mettre à jour le panier (augmenter, diminuer, supprimer)
    path('update/', views.cart_update, name='update'),

    # Vider le panier
    path('clear/', views.clear_cart, name='clear_cart'),

    # Retirer un produit du panier
    path('remove/', views.remove_from_cart, name='remove_from_cart'),

    # Compteur d'articles pour mise à jour dynamique
    path('items-count/', views.items_count, name='items_count'),
]
