from django.db import models
from django.db.models import F
from .models import *
from .views import _cart_id


from django.http import HttpResponse
# creating the counter based on the user 
def counter(request):
    cart_count = 0
    
    if 'admin' in request.path:
        return {}
    
    else:
        try:
            if request.user.is_authenticated:
                cart_count = CartItem.objects.filter(user=request.user).aggregate(total_quantity=models.Sum(F('quantity')))['total_quantity'] or 0
            else:
                cart=Cart.objects.get(cart_id=_cart_id(request))
                cart_count = CartItem.objects.filter(cart=cart).aggregate(total_quantity=models.Sum(F('quantity')))['total_quantity'] or 0
        except Cart.DoesNotExist:
            pass
    
    return {'cart_count':cart_count}