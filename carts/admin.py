from django.contrib import admin


from .models import *
# Register your models here.

class CartItemAdmin(admin.ModelAdmin):
    list_display = (
        'product',
        'cart',
        'user',
        'quantity',
        'is_active',
    )
    readonly_fields = ('cart',)
    


admin.site.register(Cart)
admin.site.register(CartItem, CartItemAdmin)