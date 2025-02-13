from decimal import Decimal
from django.conf import settings
from django.db import models
from django.db.models.signals import pre_save, post_save
from products.models import Product

User = settings.AUTH_USER_MODEL


class CartManager(models.Manager):
    def new_or_get(self, request):
        """
        Obtenez un panier existant ou créez-en un nouveau pour l'utilisateur.
        """
        cart_id = request.session.get("cart_id", None)
        qs = self.get_queryset().filter(id=cart_id)
        if qs.exists():
            cart_obj = qs.first()
            new_obj = False
            if request.user.is_authenticated and cart_obj.user is None:
                cart_obj.user = request.user
                cart_obj.save()
        else:
            cart_obj = self.new(user=request.user if request.user.is_authenticated else None)
            new_obj = True
            request.session['cart_id'] = cart_obj.id
        return cart_obj, new_obj

    def new(self, user=None):
        """
        Crée un nouveau panier pour un utilisateur.
        """
        user_obj = user if user and user.is_authenticated else None
        return self.model.objects.create(user=user_obj)


class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="cart"  # Nom unique pour éviter les conflits
    )
    products = models.ManyToManyField(
        Product,
        through="CartItem",  # Utilise le modèle intermédiaire CartItem
        blank=True,
    )
    subtotal = models.DecimalField(default=0.00, max_digits=100, decimal_places=2)
    total = models.DecimalField(default=0.00, max_digits=100, decimal_places=2)
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = CartManager()

    def __str__(self):
        return f"Cart ID: {self.id}"


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="cart_items"  # Nom unique pour éviter les conflits
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="cart_items_in_cart"  # Nom unique pour éviter les conflits
    )
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.title}"

    def get_total_item_price(self):
        return self.product.price * self.quantity


# Signal pour mettre à jour le sous-total lorsque les produits changent
def post_save_cart_item_receiver(sender, instance, **kwargs):
    """
    Met à jour le sous-total du panier après avoir sauvegardé un CartItem.
    """
    cart = instance.cart
    cart.subtotal = sum(item.get_total_item_price() for item in cart.cart_items.all())
    cart.save()


post_save.connect(post_save_cart_item_receiver, sender=CartItem)


# Signal pour calculer le total du panier avant sauvegarde (sans taxe)
def pre_save_cart_receiver(sender, instance, **kwargs):
    """
    Calcule le total du panier avant de le sauvegarder, sans appliquer de taxe.
    """
    instance.total = instance.subtotal  # Total = Sous-total (pas de taxe)

pre_save.connect(pre_save_cart_receiver, sender=Cart)