from django.urls import path
from . import views

urlpatterns = [
    # ✅ Vue principale du panier
    path('', views.cart_home, name='cart_home'),  

    # ✅ Ajouter un produit au panier
    path('add/', views.add_to_cart, name='add_to_cart'),

    # ✅ Mettre à jour le panier (ajout, suppression, modification)
    path('update/', views.cart_update, name='cart_update'),

    # ✅ Vider complètement le panier
    path('clear/', views.clear_cart, name='clear_cart'),

    # ✅ Supprimer un produit spécifique du panier
    path('remove/', views.remove_from_cart, name='remove_from_cart'),

    # ✅ Compteur d'articles dans le panier (AJAX)
    path('items-count/', views.items_count, name='items_count'),

    # ✅ Validation de la commande (checkout)
    path('checkout/', views.place_order, name='place_order'),

    # ✅ Confirmation de la commande
    path('confirmation/', views.order_confirmation, name='order_confirmation'),
]
