from django.views.generic import ListView, DetailView
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from carts.views import add_to_cart

from .models import Product
from carts.models import Cart, CartItem
from .forms import ProductForm

class ProductListView(ListView):
    model = Product
    template_name = "products/produit.html"
    context_object_name = "object_list"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        cart_obj, _ = Cart.objects.new_or_get(self.request)
        context["cart"] = cart_obj

        # Pré-calculer si chaque produit est dans le panier avec une taille
        cart_products = {}
        for item in cart_obj.cart_items.all():
            cart_products[item.product_id] = {
                'size': item.size or 'M',
                'quantity': item.quantity
            }
        context['cart_products'] = cart_products
        return context

class ProductDetailView(DetailView):
    model = Product
    template_name = "products/product_detail.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        cart_obj, _ = Cart.objects.new_or_get(self.request)
        context["cart"] = cart_obj
        return context

@user_passes_test(lambda user: user.is_authenticated and user.is_superuser)
def add_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Produit ajouté avec succès.")
            return redirect("products")
    else:
        form = ProductForm()
    return render(request, "products/add_product.html", {"form": form})

@staff_member_required(login_url='login')
def manage_products(request):
    print(f"Requête AJAX reçue pour product_id: {request.POST.get('product_id', 'None')}")
    if request.method == "POST" and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        product_id = request.POST.get("product_id")
        if not product_id:
            return JsonResponse({'success': False, 'message': 'ID de produit manquant'}, status=400)
        try:
            product = Product.objects.get(id=product_id)
            product.delete()
            return JsonResponse({'success': True, 'message': 'Produit supprimé avec succès'})
        except Product.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Produit non trouvé'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)

    products = Product.objects.all()
    return render(request, "products/manage_products.html", {"products": products})

@require_POST
def update_cart(request):
    product_id = request.POST.get('product_id')
    quantity = request.POST.get('quantity', 1)
    size = request.POST.get('size', 'M')
    action = request.POST.get('action')  # Récupérer l’action (add uniquement ici)

    try:
        if action != 'add':
            return JsonResponse({'success': False, 'message': 'Action non supportée'}, status=400)

        cart, _ = Cart.objects.new_or_get(request)
        product = get_object_or_404(Product, id=product_id)

        # Ajouter ou mettre à jour l'élément dans le panier avec la taille spécifiée
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            size=size
        )
        if created:
            cart_item.quantity = int(quantity)
        else:
            cart_item.quantity += int(quantity)
        cart_item.save()

        cart.update_totals()
        cart_count = cart.cart_items.count()
        quantity = cart_item.quantity

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'cart_count': cart_count,
                'quantity': quantity,
                'message': f"{quantity} x {product.title} (Taille: {size}) ajouté(s) au panier."
            })
        else:
            messages.success(request, f"{quantity} x {product.title} (Taille: {size}) ajouté(s) au panier.")
            return redirect(request.META.get('HTTP_REFERER', '/'))

    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Produit non trouvé'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

def products(request):
    products = Product.objects.all()
    cart_obj, _ = Cart.objects.new_or_get(request)
    return render(request, "products/produit.html", {"object_list": products, "cart": cart_obj})