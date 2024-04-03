from django.db import models


# remember the cart item consist of the product and the user ID, or session.
# so import the product, account too
from store.models import Product
from accounts.models import Account
# Create your models here.


class Cart(models.Model):
    cart_id = models.CharField(max_length=100)
    date_added = models.DateTimeField(auto_now_add=True)
    
    
    def __str__(self) -> str:
        return self.cart_id

class CartItem(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True)
    quantity = models.IntegerField()
    is_active = models.BooleanField(default=True)
    
    def sub_total(self):
        return (self.quantity * self.product.price)
    
    def __str__(self) -> str:
        return str(self.product)

