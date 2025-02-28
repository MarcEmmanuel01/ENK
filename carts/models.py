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
        cart_obj = None
        new_obj = False

        # Si l'utilisateur est authentifié, vérifiez d'abord son panier existant
        if request.user.is_authenticated:
            try:
                cart_obj = Cart.objects.get(user=request.user)
                # Si un panier existe déjà, utilisez-le même si cart_id diffère
                if cart_id != cart_obj.id:
                    request.session['cart_id'] = cart_obj.id  # Mettez à jour la session
            except Cart.DoesNotExist:
                # Aucun panier pour cet utilisateur, créez-en un
                cart_obj = self.new(user=request.user)
                new_obj = True
                request.session['cart_id'] = cart_obj.id
        else:
            # Utilisateur non authentifié : récupérez ou créez un panier anonyme
            qs = self.get_queryset().filter(id=cart_id)
            if qs.exists():
                cart_obj = qs.first()
            else:
                cart_obj = self.new(user=None)
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


# Ajout des modèles Order et OrderItem
class Order(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    order_identifier = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        unique=True
    )
    fullname = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    address = models.TextField()
    notes = models.TextField(blank=True, null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        default="pending",
        choices=[("pending", "En attente"), ("shipped", "Expédiée"), ("delivered", "Livrée")]
    )

    def __str__(self):
        return f"Commande {self.id} - {self.fullname}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.title} (Commande {self.order.id})"