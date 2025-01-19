from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from products.models import Product
from .models import Cart, CartItem



def cart_home(request):
    """
    Affiche les produits dans le panier.
    """
    cart, _ = Cart.objects.new_or_get(request)
    cart_items = CartItem.objects.filter(cart=cart)
    return render(request, "carts/home.html", {'cart': cart, 'cart_items': cart_items})


def add_to_cart(request):
    """
    Ajoute un produit au panier ou met à jour la quantité.
    """
    if request.method == "POST":
        product_id = request.POST.get("product_id")
        quantity = int(request.POST.get("quantity", 1))

        # Validation de la quantité
        if quantity <= 0:
            messages.error(request, "Veuillez sélectionner une quantité valide.")
            return redirect(request.META.get('HTTP_REFERER', '/'))

        # Récupérer ou créer un panier
        cart, _ = Cart.objects.new_or_get(request)
        product = get_object_or_404(Product, id=product_id)

        # Ajouter ou mettre à jour l'article
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if created:
            cart_item.quantity = quantity
        else:
            cart_item.quantity += quantity
        cart_item.save()

        # Mise à jour du nombre total d'articles dans la session
        request.session['cart_items'] = CartItem.objects.filter(cart=cart).count()

        # Réponse AJAX (si applicable)
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'quantity': cart_item.quantity})

        messages.success(request, f"{quantity} x {product.title} ajouté(s) au panier.")
        return redirect(request.META.get('HTTP_REFERER', '/'))  # Retourne à la page précédente
    return redirect("products")



# Mettre à jour un produit du panier
def cart_update(request):
    if request.method == "POST":
        product_id = request.POST.get("product_id")
        action = request.POST.get("action")  # "increase", "decrease", "remove"
        cart, _ = Cart.objects.new_or_get(request)

        product = get_object_or_404(Product, id=product_id)
        cart_item = CartItem.objects.filter(cart=cart, product=product).first()

        if cart_item:
            if action == "increase":
                cart_item.quantity += 1
                cart_item.save()
            elif action == "decrease":
                if cart_item.quantity > 1:
                    cart_item.quantity -= 1
                    cart_item.save()
                else:
                    cart_item.delete()
            elif action == "remove":
                cart_item.delete()

        # Mise à jour de la session
        request.session['cart_items'] = CartItem.objects.filter(cart=cart).count()

        # Réponse AJAX pour mise à jour dynamique
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True})

        return redirect("cart")
    return redirect("cart")


# Vider le panier
def clear_cart(request):
    cart, _ = Cart.objects.new_or_get(request)
    CartItem.objects.filter(cart=cart).delete()
    cart.subtotal = 0
    cart.total = 0
    cart.save()
    request.session['cart_items'] = 0

    # Réponse AJAX pour les requêtes dynamiques
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True})

    return redirect("cart")


# Compteur d'articles dans le panier
def items_count(request):
    cart, _ = Cart.objects.new_or_get(request)
    total_items = sum(item.quantity for item in CartItem.objects.filter(cart=cart))
    return JsonResponse({"count": total_items})


# Retirer un produit du panier
def remove_from_cart(request):
    if request.method == "POST":
        product_id = request.POST.get("product_id")
        cart, _ = Cart.objects.new_or_get(request)

        cart_item = CartItem.objects.filter(cart=cart, product_id=product_id).first()
        if cart_item:
            cart_item.delete()
            messages.success(request, "Produit retiré du panier.")
        else:
            messages.error(request, "Ce produit n'est pas dans votre panier.")

        return redirect("cart")
    return redirect("cart")
