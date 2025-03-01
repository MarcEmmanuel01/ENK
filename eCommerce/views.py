from django.contrib.auth import authenticate, login, get_user_model
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ContactForm
from django.views.generic import TemplateView
from products.models import Product
from carts.models import Cart
from django.views.decorators.http import require_POST

# Vue de la page d'accueil
class HomePage(TemplateView):
    template_name = "home_page.html"
    
    def get_context_data(self, *args, **kwargs):
        context = super(HomePage, self).get_context_data(*args, **kwargs)
        cart_obj, new_obj = Cart.objects.new_or_get(self.request)
        context['cart'] = cart_obj
        context['cart_count'] = cart_obj.products.count()  # Nombre d'articles dans le panier
        context['products'] = Product.objects.all()  # Liste des produits (optionnel)
        return context

# Vue "À propos"
def about_page(request):
    cart_obj, new_obj = Cart.objects.new_or_get(request)
    context = {
        "title": "About Page",
        "cart_count": cart_obj.products.count()
    }
    return render(request, "about_page.html", context)

# Vue "Contact"
def contact_page(request):
    contact_form = ContactForm(request.POST or None)
    cart_obj, new_obj = Cart.objects.new_or_get(request)
    context = {
        "title": "Contact",
        "form": contact_form,
        "cart_count": cart_obj.products.count()
    }
    
    if request.method == "POST":
        if contact_form.is_valid():
            print(contact_form.cleaned_data)
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({"message": "Thank you for your submission"}, status=200)
            else:
                messages.success(request, "Votre message a été envoyé avec succès !")
                return redirect("contact")
    
        if contact_form.errors:
            errors = contact_form.errors.as_json()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return HttpResponse(errors, status=400, content_type='application/json')
            else:
                messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")

    return render(request, "contact_page.html", context)

# Vue AJAX pour ajouter au panier
@require_POST
def add_to_cart(request, product_id):
    try:
        cart_obj, new_obj = Cart.objects.new_or_get(request)
        product = Product.objects.get(id=product_id)
        cart_obj.products.add(product)  # Ajouter le produit
        cart_count = cart_obj.products.count()  # Nouveau total
        return JsonResponse({'cart_count': cart_count})
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Produit non trouvé'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# Vue pour la page du panier
def cart_page(request):
    cart_obj, new_obj = Cart.objects.new_or_get(request)
    context = {
        "cart": cart_obj,
        "cart_count": cart_obj.products.count()
    }
    return render(request, "cart_page.html", context)