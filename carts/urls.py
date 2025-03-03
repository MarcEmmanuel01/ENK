from django.urls import path
from . import views

urlpatterns = [
    path('', views.cart_home, name='cart_home'),
    path('add/', views.add_to_cart, name='add_to_cart'),
    path('update/', views.cart_update, name='cart_update'),
    path('clear/', views.clear_cart, name='clear_cart'),
    path('remove/', views.remove_from_cart, name='remove_from_cart'),
    path('items-count/', views.items_count, name='items_count'),
    path('checkout/', views.place_order, name='place_order'),
    path('confirmation/', views.order_confirmation, name='order_confirmation'),
]