from django import forms

from .models import Category, Product


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = [
            'category_name',
        ]
        
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'category',
            'product_name',
            'description',
            'price',
            'image',
            'stock',
        ]