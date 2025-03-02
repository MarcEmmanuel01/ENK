# products/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # URL pour ajouter un produit (admin uniquement)
    path('add/', views.add_product, name='add_product'),
    # URL pour gérer les produits (admin uniquement)
    path('manage/', views.manage_products, name='manage_products'),
    # URL pour mettre à jour le panier via AJAX (placé avant <slug:slug>/)
    path('update-cart/', views.update_cart, name='update_cart'),
    # URL pour la liste des produits
    path('', views.ProductListView.as_view(), name='products'),
    # URL pour les détails d'un produit (basée sur le slug, placé en dernier)
    path('<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
]