from django.db import models
from django.urls import reverse
from django.db.models.signals import pre_save
from django.db.models import Q
from .utils import unique_slug_generator

class ProductQuerySet(models.query.QuerySet):
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
    price = models.FloatField(max_length=120, null=True)
    discount_price = models.FloatField(max_length=120, blank=True, null=True)
    size = models.CharField(max_length=100, blank=True)
    color = models.CharField(max_length=100, blank=True)
    image = models.ImageField(default='default.png', upload_to='image')
    description = models.TextField(blank=True)
    featured = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)

    objects = ProductManager()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'slug': self.slug})


def product_pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)


pre_save.connect(product_pre_save_receiver, sender=Product)


class Produit(models.Model):
    nom = models.CharField(max_length=200)
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    date_ajout = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom
