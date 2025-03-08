from django.urls import path
from . import views

urlpatterns = [
    path('', views.cart_home, name='cart_home'),
    path('add/', views.add_to_cart, name='add_to_cart'),
    path('update/', views.cart_update, name='cart_update'),
    path('clear/', views.clear_cart, name='clear_cart'),
    path('items_count/', views.items_count, name='items_count'),
    path('remove/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.place_order, name='place_order'),
    path('confirmation/', views.order_confirmation, name='order_confirmation'),
    # Vues Admin
    path('admin/orders/', views.admin_orders, name='admin_orders'),  # Tableau de bord
    path('admin/orders/list/', views.admin_orders_list, name='admin_orders_list'),
    path('admin/clients/', views.admin_clients, name='admin_clients'),
    path('admin/recent-logins/', views.admin_recent_logins, name='admin_recent_logins'),
    path('admin/contact-messages/', views.admin_contact_messages, name='admin_contact_messages'),
    path('admin/orders/update/<int:order_id>/', views.update_order_status, name='update_order_status'),
    path('admin/orders/detail/<int:order_id>/', views.admin_order_detail, name='admin_order_detail'),
]