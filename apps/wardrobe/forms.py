from django import forms
from .models import WardrobeItem

class WardrobeItemForm(forms.ModelForm):
    class Meta:
        model = WardrobeItem
        fields = ['item_type', 'category', 'occasion', 'season', 'color', 'image']
        widgets = {
            'item_type': forms.TextInput(attrs={'placeholder': 'e.g., Blue Shirt'}),
            'color': forms.TextInput(attrs={'placeholder': 'Optional'}),
        }
