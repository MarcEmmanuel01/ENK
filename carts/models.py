from decimal import Decimal
from django.conf import settings
from django.db import models
from django.db.models.signals import pre_save, post_save
from products.models import Product

User = settings.AUTH_USER_MODEL

class CartManager(models.Manager):
    def new_or_get(self, request):
        cart_id = request.session.get("cart_id", None)
        cart_obj = None
        new_obj = False

        if request.user.is_authenticated:
            cart_obj, created = self.get_or_create(
                user=request.user,
                active=True
            )
            if created or (cart_id and str(cart_id) != str(cart_obj.id)):
                request.session['cart_id'] = cart_obj.id
        else:
            if cart_id:
                qs = self.filter(id=cart_id, active=True)
                if qs.exists():
                    cart_obj = qs.first()
            if not cart_obj:
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
        return f"Panier ID: {self.id} ({'Actif' if self.active else 'Inactif'})"

    def update_totals(self):
        if self.pk:
            self.subtotal = sum(
                item.get_total_item_price() for item in self.cart_items.all()
            ) or Decimal('0.00')
            self.total = self.subtotal
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

    class Meta:
        unique_together = ('cart', 'product', 'size')

    def __str__(self):
        size_str = f" (Taille: {self.size})" if self.size else ""
        return f"{self.quantity} x {self.product.title}{size_str}"

    def get_total_item_price(self):
        return Decimal(self.product.price) * Decimal(self.quantity)

    get_total = get_total_item_price

def post_save_cart_item_receiver(sender, instance, **kwargs):
    if instance.cart.pk:
        instance.cart.update_totals()

post_save.connect(post_save_cart_item_receiver, sender=CartItem)

def pre_save_cart_receiver(sender, instance, **kwargs):
    if instance.pk and instance.subtotal != instance.total:
        instance.total = instance.subtotal

pre_save.connect(pre_save_cart_receiver, sender=Cart)

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
        choices=[
            ("pending", "En attente"),
            ("shipped", "Expédiée"),
            ("delivered", "Livrée")
        ]
    )

    def __str__(self):
        return f"Commande {self.id} - {self.fullname}"

class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    size = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        size_str = f" (Taille: {self.size})" if self.size else ""
        return f"{self.quantity} x {self.product.title}{size_str} (Commande {self.order.id})"