from django.db import models
from django.urls import reverse
from django.core.validators import FileExtensionValidator
from django.contrib.auth.models import AbstractUser
from .validators import ASCIIUsernameValidator
from django.contrib.auth import get_user_model
from django.conf import settings

class User(AbstractUser):
    is_customer = models.BooleanField(default=False)
    phone = models.CharField(max_length=60, blank=True, null=True)
    address = models.CharField(max_length=60, blank=True, null=True)
    picture = models.ImageField(upload_to='profile_pictures', default='default.png', null=True)
    email = models.EmailField(null=True)

    username_validator = ASCIIUsernameValidator()

    # def __str__(self):
    #     return "{} {}".format(self.first_name, self.last_name, self.email)

    @property
    def get_full_name(self):
        full_name = self.username
        if self.first_name and self.last_name:
            full_name = self.first_name + " " + self.last_name
        return full_name

    def get_absolute_url(self):
        return reverse('profile_single', kwargs={'id': self.id})






class ContactMessage(models.Model):
    fullname = models.CharField(max_length=255)
    email = models.EmailField(max_length=254)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL
    )

    def __str__(self):
        return f"{self.fullname} ({self.email})"
