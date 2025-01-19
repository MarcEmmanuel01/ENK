from django.urls import path
from .views import contact_view
from .views import subscribe_newsletter

urlpatterns = [
    path("contact/", contact_view, name="contact"),
    
    path("subscribe/", subscribe_newsletter, name="subscribe"),
]
