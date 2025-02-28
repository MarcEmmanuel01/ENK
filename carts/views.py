from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from products.models import Product
from .models import Cart, CartItem, Order, OrderItem
from django.utils.crypto import get_random_string

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

        if quantity <= 0:
            messages.error(request, "Veuillez sélectionner une quantité valide.")
            return redirect(request.META.get('HTTP_REFERER', '/'))

        cart, _ = Cart.objects.new_or_get(request)
        product = get_object_or_404(Product, id=product_id)

        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if created:
            cart_item.quantity = quantity
        else:
            cart_item.quantity += quantity
        cart_item.save()

        request.session['cart_items'] = CartItem.objects.filter(cart=cart).count()

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'quantity': cart_item.quantity})

        messages.success(request, f"{quantity} x {product.title} ajouté(s) au panier.")
        return redirect(request.META.get('HTTP_REFERER', '/'))
    return redirect("products")

def cart_update(request):
    if request.method == "POST":
        product_id = request.POST.get("product_id")
        action = request.POST.get("action")
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

        request.session['cart_items'] = CartItem.objects.filter(cart=cart).count()

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True})

        return redirect("cart")
    return redirect("cart")

def clear_cart(request):
    cart, _ = Cart.objects.new_or_get(request)
    CartItem.objects.filter(cart=cart).delete()
    cart.subtotal = 0
    cart.total = 0
    cart.save()
    request.session['cart_items'] = 0

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True})

    return redirect("cart")

def items_count(request):
    cart, _ = Cart.objects.new_or_get(request)
    total_items = sum(item.quantity for item in CartItem.objects.filter(cart=cart))
    return JsonResponse({"count": total_items})

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

def place_order(request):
    cart, _ = Cart.objects.new_or_get(request)
    cart_items = CartItem.objects.filter(cart=cart)

    if request.method == "POST":
        fullname = request.POST.get("fullname")
        phone = request.POST.get("phone")
        email = request.POST.get("email", "")
        city = request.POST.get("city")
        district = request.POST.get("district")
        address = request.POST.get("address")
        notes = request.POST.get("notes", "")

        if not cart_items.exists():
            messages.error(request, "Votre panier est vide.")
            return redirect("cart")

        if request.user.is_authenticated:
            user = request.user
            order_identifier = None
        else:
            user = None
            order_identifier = get_random_string(10)

        order = Order.objects.create(
            user=user,
            order_identifier=order_identifier,
            fullname=fullname,
            phone=phone,
            email=email,
            city=city,
            district=district,
            address=address,
            notes=notes,
            total_price=cart.total + 1000
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price * item.quantity
            )

        cart_items.delete()
        cart.subtotal = 0
        cart.total = 0
        cart.save()
        request.session['cart_items'] = 0
        if 'cart_id' in request.session:
            del request.session['cart_id']

        messages.success(request, "Votre commande a été passée avec succès !")
        return redirect("order_confirmation")

    return render(request, "carts/checkout.html", {"cart": cart, "cart_items": cart_items})

def order_confirmation(request):
    """
    Affiche une page de confirmation après une commande réussie.
    """
    if request.user.is_authenticated:
        last_order = Order.objects.filter(user=request.user).order_by('-created_at').first()
    else:
        last_order = None  # Pour les utilisateurs anonymes, pas de suivi direct ici
    return render(request, "carts/order_confirmation.html", {"order": last_order})