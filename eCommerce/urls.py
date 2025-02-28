from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views  # Import des vues locales si elles existent (ex: HomePage, about_page)
from carts.views import cart_home  # Vue principale du panier

urlpatterns = [
    # Page d'accueil
    path('', views.HomePage.as_view(), name='home'),
    
    # À propos
    path('about/', views.about_page, name='about'),
    
    # Page de contact
    path('contact/', views.contact_page, name='contact'),
    
    # Comptes utilisateurs
    path('accounts/', include('accounts.urls')),  
    
    # Produits
    path('products/', include('products.urls')),  # Routes pour l'application "products"
    
    # Tags
    path('tags/', include('tags.urls')),  # Routes pour l'application "tags"
    
    # Recherche
    path('search/', include('search.urls')),  # Routes pour l'application "search"
    
    # Panier
    path('cart/', include('carts.urls')),  # Routes pour l'application "carts"
    


    # Administration
    path('admin/', admin.site.urls),  # Administration Django
]

# Ajout des fichiers statiques et médias en mode DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
