from django.urls import path
from . import views

urlpatterns = [
    # URL pour ajouter un produit
    path('add/', views.add_product, name='add_product'),

    # URL pour gérer les produits
    path('manage/', views.manage_products, name='manage_products'),

    # URL pour la liste des produits
    path('', views.ProductListView.as_view(), name='products'),

 path('', views.ProductListView.as_view(), name='product_list'),  # Le nom ici est important
    path('<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
]
