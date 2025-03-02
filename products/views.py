from django.views.generic import ListView, DetailView
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import Product
from carts.models import Cart
from .forms import ProductForm


# ✅ Vue pour la liste des produits
class ProductListView(ListView):
    model = Product
    template_name = "products/produit.html"
    context_object_name = "object_list"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        cart_obj, _ = Cart.objects.new_or_get(self.request)
        context["cart"] = cart_obj
        return context


# ✅ Vue pour les détails d'un produit
class ProductDetailView(DetailView):
    model = Product
    template_name = "products/product_detail.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        cart_obj, _ = Cart.objects.new_or_get(self.request)
        context["cart"] = cart_obj
        return context


# ✅ Vue pour ajouter un produit (réservée aux administrateurs)
@user_passes_test(lambda user: user.is_authenticated and user.is_superuser)
def add_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Produit ajouté avec succès.")
            return redirect("products")  # Redirige vers la liste des produits
    else:
        form = ProductForm()
    return render(request, "products/add_product.html", {"form": form})


# ✅ Vue pour gérer les produits (réservée aux administrateurs)
@staff_member_required
def manage_products(request):
    products = Product.objects.all()
    
    if request.method == "POST" and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Gestion AJAX pour la suppression
        product_id = request.POST.get("product_id")
        product = get_object_or_404(Product, id=product_id)
        product.delete()
        return JsonResponse({'success': True, 'message': 'Produit supprimé avec succès'})

    return render(request, "products/manage_products.html", {"products": products})


# ✅ Vue AJAX pour ajouter ou retirer un produit du panier
@require_POST
def update_cart(request):
    product_id = request.POST.get('product_id')
    
    try:
        product = Product.objects.get(id=product_id)
        cart_obj, _ = Cart.objects.new_or_get(request)

        if product in cart_obj.products.all():
            cart_obj.products.remove(product)
            action = 'removed'
        else:
            cart_obj.products.add(product)
            action = 'added'
        
        return JsonResponse({
            'success': True,
            'message': f'Produit {action} avec succès',
            'cart_count': cart_obj.products.count(),
            'is_in_cart': product in cart_obj.products.all()
        })

    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Produit non trouvé'}, status=404)
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


# ✅ Vue alternative pour afficher la liste des produits
def products(request):
    products = Product.objects.all()
    cart_obj, _ = Cart.objects.new_or_get(request)
    return render(request, "products/produit.html", {"object_list": products, "cart": cart_obj})