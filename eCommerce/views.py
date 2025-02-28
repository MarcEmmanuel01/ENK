from django.contrib.auth import authenticate, login, get_user_model
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages  # Ajouté pour messages.success
from .forms import ContactForm
from django.views.generic import TemplateView
from products.models import Product
from carts.models import Cart

class HomePage(TemplateView):
    template_name = "home_page.html"
    
    def get_context_data(self, *args, **kwargs):
        context = super(HomePage, self).get_context_data(*args, **kwargs)
        cart_obj, new_obj = Cart.objects.new_or_get(self.request)
        context['cart'] = cart_obj
        return context

def about_page(request):
    context = {
        "title": "About Page"
    }
    return render(request, "about_page.html", context)

def contact_page(request):
    contact_form = ContactForm(request.POST or None)
    context = {
        "title": "Contact",
        "form": contact_form
    }
    
    if request.method == "POST":
        if contact_form.is_valid():
            print(contact_form.cleaned_data)
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({"message": "Thank you for your submission"}, status=200)
            else:
                # Ajouter un message de succès pour les utilisateurs non-AJAX
                messages.success(request, "Votre message a été envoyé avec succès !")
                return redirect("contact")  # Redirige pour éviter resoumission
    
        if contact_form.errors:
            errors = contact_form.errors.as_json()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return HttpResponse(errors, status=400, content_type='application/json')
            else:
                # Ajouter un message d'erreur pour les utilisateurs non-AJAX
                messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")

    return render(request, "contact_page.html", context)