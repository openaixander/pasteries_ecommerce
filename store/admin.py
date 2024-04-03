from django.contrib import admin
from .models import Product, Category
# Register your models here.

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {
        'slug': ('category_name',)
    }

class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {
        'slug': ('product_name',)
    }
    list_display = (
        'product_name',
        'category',
        'price',
        'stock',
        'image',
        'is_available',
        'created_at',
    )

admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
