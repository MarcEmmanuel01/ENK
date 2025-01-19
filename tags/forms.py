from django import forms
from .models import ContactMessage

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["fullname", "email", "content"]
        widgets = {
            "fullname": forms.TextInput(attrs={"class": "form-control", "placeholder": "Votre nom complet"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Votre email"}),
            "content": forms.Textarea(attrs={"class": "form-control", "placeholder": "Votre message"}),
        }
