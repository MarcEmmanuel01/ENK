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

        if request.user.is_authenticated:
            cart_obj, created = self.get_or_create(user=request.user)
            if created or cart_id != cart_obj.id:
                request.session['cart_id'] = cart_obj.id
        else:
            qs = self.filter(id=cart_id)
            if qs.exists():
                cart_obj = qs.first()
            else:
                cart_obj = self.create(user=None)
                new_obj = True
                request.session['cart_id'] = cart_obj.id

        return cart_obj, new_obj


class Cart(models.Model):
    user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="carts"
    )
    products = models.ManyToManyField(
        Product,
        through="CartItem",
        blank=True,
    )
    subtotal = models.DecimalField(default=0.00, max_digits=10, decimal_places=2)
    total = models.DecimalField(default=0.00, max_digits=10, decimal_places=2)
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    objects = CartManager()

    def __str__(self):
        return f"Cart ID: {self.id}"

    def update_totals(self):
        """
        Met à jour le sous-total et total du panier.
        """
        self.subtotal = sum(item.get_total_item_price() for item in self.cart_items.all())
        self.total = self.subtotal  # Ajout d'éventuelles taxes ici si nécessaire
        self.save()


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="cart_items"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="cart_items_in_cart"
    )
    quantity = models.PositiveIntegerField(default=1)
    size = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return f"{self.quantity} x {self.product.title}"

    def get_total_item_price(self):
        """Calcule le prix total de cet article."""
        return Decimal(self.product.price) * Decimal(self.quantity)

    # Alias pour une utilisation claire dans le template
    get_total = get_total_item_price


# Signal pour mettre à jour le sous-total du panier après modification d'un `CartItem`
def post_save_cart_item_receiver(sender, instance, **kwargs):
    """
    Met à jour le sous-total du panier après ajout ou modification d'un article.
    """
    instance.cart.update_totals()


post_save.connect(post_save_cart_item_receiver, sender=CartItem)


# Signal pour éviter les erreurs d'accès aux `cart_items` avant que `Cart` ait une clé primaire
def pre_save_cart_receiver(sender, instance, **kwargs):
    """
    Assure que le total est mis à jour avant sauvegarde.
    """
    if instance.pk:  # Vérifie que l'instance a bien une clé primaire
        instance.total = instance.subtotal  # Pas de taxe appliquée pour l'instant


pre_save.connect(pre_save_cart_receiver, sender=Cart)


# Modèles pour la gestion des commandes
class Order(models.Model):
    user = models.ForeignKey(
        User,
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