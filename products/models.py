from django.db import models
from django.urls import reverse
from django.db.models.signals import pre_save
from django.db.models import Q
from .utils import unique_slug_generator

class ProductQuerySet(models.QuerySet):
    def active(self):
        return self.filter(active=True)

    def featured(self):
        return self.filter(featured=True, active=True)

    def search(self, query):
        lookups = (
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(price__icontains=query)
        )
        return self.filter(lookups).distinct()


class ProductManager(models.Manager):
    def get_queryset(self):
        return ProductQuerySet(self.model, using=self._db)

    def all(self):
        return self.get_queryset().active()

    def featured(self):
        return self.get_queryset().featured()

    def get_by_id(self, id):
        qs = self.get_queryset().filter(id=id)
        if qs.count() == 1:
            return qs.first()
        return None

    def search(self, query):
        return self.get_queryset().active().search(query)


class Product(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(blank=True, unique=True)
    brand = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True)  # Changé de FloatField à DecimalField
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    size = models.CharField(max_length=100, blank=True)  # Peut-être remplacé par un champ choix si pertinent
    color = models.CharField(max_length=100, blank=True)
    image = models.ImageField(default='default.png', upload_to='image')
    description = models.TextField(blank=True)
    featured = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = ProductManager()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'slug': self.slug})

    def is_in_cart(self, cart):
        """Vérifie si le produit est dans le panier, en tenant compte de la taille si applicable."""
        from carts.models import CartItem  # Import différé pour éviter circularité
        return CartItem.objects.filter(cart=cart, product=self).exists()


def product_pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)


pre_save.connect(product_pre_save_receiver, sender=Product)