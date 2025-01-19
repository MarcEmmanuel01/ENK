from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'title', 'brand', 'price', 'discount_price', 
            'size', 'color', 'image', 'description', 'featured', 'active'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Titre'}),
            'brand': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Marque'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Prix'}),
            'discount_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Prix réduit'}),
            'size': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Taille'}),
            'color': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Couleur'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Description'}),
        }
