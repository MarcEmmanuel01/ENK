from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, update_session_auth_hash
from .forms import RegistrationForm, ProfileUpdateForm, PasswordChangeForm
from .models import User
from .forms import ContactForm  # Assurez-vous que le formulaire est importé
from .models import ContactMessage
from django.utils.timezone import now
from accounts.models import ContactMessage
from accounts.forms import ContactForm

# ########################################################
# Profile Views
# ########################################################
@login_required
def profile(request):
    """
    Affiche le profil de l'utilisateur connecté.
    """
    if hasattr(request.user, 'is_customer') and request.user.is_customer:
        # Personnalisez ici si des données spécifiques doivent être affichées pour les clients
        context = {
            'title': request.user.get_full_name(),
        }
    else:
        staff = User.objects.filter(is_superuser=True)
        context = {
            'title': request.user.get_full_name(),
            'staff': staff,
        }

    return render(request, 'accounts/profile.html', context)


# ########################################################
# Profile Update View
# ########################################################
@login_required
def profile_update(request):
    """
    Permet à l'utilisateur de mettre à jour son profil.
    """
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Votre profil a été mis à jour avec succès.')
            return redirect('profile')
        else:
            messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')
    else:
        form = ProfileUpdateForm(instance=request.user)

    return render(request, 'accounts/profile_setting.html', {
        'title': 'Paramètres du profil',
        'form': form,
    })


# ########################################################
# Change Password View
# ########################################################
@login_required
def change_password(request):
    """
    Permet à l'utilisateur de changer son mot de passe.
    """
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Maintient l'utilisateur connecté
            messages.success(request, 'Votre mot de passe a été mis à jour avec succès.')
            return redirect('profile')
        else:
            messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'accounts/password_change.html', {
        'title': 'Changer de mot de passe',
        'form': form,
    })


# ########################################################
# Registration View
# ########################################################
def registration_page(request):
    """
    Permet à un nouvel utilisateur de s'inscrire.
    """
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request, "Votre compte a été créé avec succès. Vous pouvez maintenant vous connecter."
            )
            return redirect('login')
        else:
            messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')
    else:
        form = RegistrationForm()

    return render(request, 'accounts/register.html', {
        'title': 'Inscription',
        'form': form,
    })


# ########################################################
# Logout View
# ########################################################
def logout_view(request):
    """
    Déconnecte l'utilisateur et redirige vers la page d'accueil.
    """
    logout(request)
    return redirect('home')  # Redirige vers la page d'accueil



# ########################################################
# send request formulaire
# ########################################################



def contact_page(request):
    form = ContactForm(request.POST or None)
    success = False

    if form.is_valid():
        # Sauvegarde dans la base de données
        ContactMessage.objects.create(
            fullname=form.cleaned_data["fullname"],
            email=form.cleaned_data["email"],
            content=form.cleaned_data["content"],
            created_at=now(),  # Date actuelle
            user=request.user if request.user.is_authenticated else None
        )
        messages.success(request, "Votre message a été envoyé avec succès.")
        success = True
        form = ContactForm()  # Réinitialisez le formulaire

    return render(request, "contact_page.html", {"form": form, "success": success})
