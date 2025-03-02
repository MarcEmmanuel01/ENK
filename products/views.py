from django.views.generic import ListView, DetailView
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from carts.views import add_to_cart

from .models import Product
from carts.models import Cart
from .forms import ProductForm

class ProductListView(ListView):
    model = Product
    template_name = "products/produit.html"
    context_object_name = "object_list"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        cart_obj, _ = Cart.objects.new_or_get(self.request)
        context["cart"] = cart_obj
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

@staff_member_required
def manage_products(request):
    products = Product.objects.all()
    
    if request.method == "POST" and request.headers.get("X-Requested-With") == "XMLHttpRequest":
        product_id = request.POST.get("product_id")
        product = get_object_or_404(Product, id=product_id)
        product.delete()
        return JsonResponse({"success": True, "message": "Produit supprimé avec succès"})

    return render(request, "products/manage_products.html", {"products": products})

@require_POST
def update_cart(request):
    product_id = request.POST.get("product_id")
    quantity = request.POST.get("quantity", 1)
    size = request.POST.get("size", "M")

    try:
        request.POST = request.POST.copy()
        request.POST["product_id"] = product_id
        request.POST["quantity"] = quantity
        request.POST["size"] = size

        response = add_to_cart(request)

        if isinstance(response, JsonResponse):
            data = response.getvalue().decode("utf-8")
            import json
            json_data = json.loads(data)
            cart_obj, _ = Cart.objects.new_or_get(request)
            json_data["cart_count"] = cart_obj.cart_items.count()
            return JsonResponse(json_data)

        return redirect("cart_home")

    except Product.DoesNotExist:
        return JsonResponse({"success": False, "message": "Produit non trouvé"}, status=404)
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)

def products(request):
    products = Product.objects.all()
    cart_obj, _ = Cart.objects.new_or_get(request)
    return render(request, "products/produit.html", {"object_list": products, "cart": cart_obj})
