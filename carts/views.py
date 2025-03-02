from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from products.models import Product
from .models import Cart, CartItem, Order, OrderItem
from django.utils.crypto import get_random_string
from django.views.decorators.http import require_POST


# ✅ Vue principale du panier
def cart_home(request):
    cart, _ = Cart.objects.new_or_get(request)
    cart_items = cart.cart_items.all()
    return render(request, "carts/home.html", {'cart': cart, 'cart_items': cart_items})


# ✅ Ajouter un produit au panier
@require_POST
def add_to_cart(request):
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

    cart.update_totals()
    request.session['cart_items'] = cart.cart_items.count()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'quantity': cart_item.quantity})

    messages.success(request, f"{quantity} x {product.title} ajouté(s) au panier.")
    return redirect(request.META.get('HTTP_REFERER', '/'))


# ✅ Mettre à jour le panier (augmenter, diminuer, supprimer)
@require_POST
def cart_update(request):
    product_id = request.POST.get("product_id")
    action = request.POST.get("action")
    cart, _ = Cart.objects.new_or_get(request)

    cart_item = CartItem.objects.filter(cart=cart, product__id=product_id).first()
    if not cart_item:
        return JsonResponse({'success': False, 'message': "Article non trouvé dans le panier"}, status=404)

    if action == "increase":
        cart_item.quantity += 1
    elif action == "decrease":
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
        else:
            cart_item.delete()
    elif action == "remove":
        cart_item.delete()

    cart.update_totals()
    request.session['cart_items'] = cart.cart_items.count()

    return JsonResponse({'success': True, 'cart_total': cart.total})


# ✅ Vider le panier
def clear_cart(request):
    cart, _ = Cart.objects.new_or_get(request)
    cart.cart_items.all().delete()
    cart.subtotal = 0
    cart.total = 0
    cart.save()
    request.session['cart_items'] = 0

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True})

    messages.success(request, "Le panier a été vidé.")
    return redirect("cart_home")


# ✅ Obtenir le nombre total d'articles dans le panier
def items_count(request):
    cart, _ = Cart.objects.new_or_get(request)
    total_items = sum(item.quantity for item in cart.cart_items.all())
    return JsonResponse({"count": total_items})


# ✅ Supprimer un produit du panier
@require_POST
def remove_from_cart(request):
    product_id = request.POST.get("product_id")
    cart, _ = Cart.objects.new_or_get(request)

    cart_item = CartItem.objects.filter(cart=cart, product_id=product_id).first()
    if cart_item:
        cart_item.delete()
        cart.update_totals()
        messages.success(request, "Produit retiré du panier.")
    else:
        messages.error(request, "Ce produit n'est pas dans votre panier.")

    return redirect("cart_home")


# ✅ Passer une commande
def place_order(request):
    cart, _ = Cart.objects.new_or_get(request)
    cart_items = cart.cart_items.all()

    if not cart_items.exists():
        messages.error(request, "Votre panier est vide.")
        return redirect("cart_home")

    if request.method == "POST":
        fullname = request.POST.get("fullname")
        phone = request.POST.get("phone")
        email = request.POST.get("email", "")
        city = request.POST.get("city")
        district = request.POST.get("district")
        address = request.POST.get("address")
        notes = request.POST.get("notes", "")

        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            order_identifier=get_random_string(10) if not request.user.is_authenticated else None,
            fullname=fullname,
            phone=phone,
            email=email,
            city=city,
            district=district,
            address=address,
            notes=notes,
            total_price=cart.total + 1000  # Ajout des frais de livraison
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


# ✅ Confirmation de commande
def order_confirmation(request):
    last_order = None
    if request.user.is_authenticated:
        last_order = Order.objects.filter(user=request.user).order_by('-created_at').first()
    return render(request, "carts/order_confirmation.html", {"order": last_order})