from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ContactForm
from .models import Newsletter


def contact_view(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()  # Sauvegarde des données dans la base
            messages.success(request, "Votre message a été envoyé avec succès !")
            return redirect("contact")
        else:
            messages.error(request, "Veuillez corriger les erreurs.")
    else:
        form = ContactForm()

    return render(request, "tags/contact.html", {"form": form})





def subscribe_newsletter(request):
    if request.method == "POST":
        email = request.POST.get("email")
        if email:
            if not Newsletter.objects.filter(email=email).exists():
                Newsletter.objects.create(email=email)
                messages.success(request, "Vous êtes abonné à notre newsletter avec succès !")
            else:
                messages.info(request, "Cet e-mail est déjà abonné.")
        else:
            messages.error(request, "Veuillez fournir une adresse e-mail valide.")
        return redirect("home")  # Redirigez vers la page principale ou une autre page
    return render(request, "tags/subscribe.html")
