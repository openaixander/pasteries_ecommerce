from django.contrib import admin
from .models import Order, Payment,OrderProduct
# Register your models here.

class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    readonly_fields = (
        'payment',
        'user',
        'product',
        'quantity',
        'product_price',
        'ordered'
    )
    extra = 0
    

class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'first_name',
        'last_name',
        'phone',
        'email',
        'city',
        'state',
        'status',
        'is_ordered',
    )
    list_per_page = 20
    inlines = [OrderProductInline]

admin.site.register(Payment)
admin.site.register(OrderProduct)
admin.site.register(Order, OrderAdmin)

