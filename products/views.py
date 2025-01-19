from django.views.generic import ListView, DetailView
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from .models import Product
from carts.models import Cart  # Import direct du modèle Cart
from .forms import ProductForm


class ProduitListView(ListView):
    model = Product
    template_name = "products/produit.html"
    context_object_name = "object_list"


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
            return redirect("product_list")
    else:
        form = ProductForm()
    return render(request, "products/add_product.html", {"form": form})


@staff_member_required
def manage_products(request):
    products = Product.objects.all()
    if request.method == "POST":
        product_id = request.POST.get("product_id")
        product = get_object_or_404(Product, id=product_id)
        product.delete()
        messages.success(request, "Produit supprimé avec succès.")
        return redirect("manage_products")
    return render(request, "products/manage_products.html", {"products": products})


def product_list(request):
    products = Product.objects.all()
    return render(request, "products/produit.html", {"object_list": products})
