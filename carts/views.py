from django.shortcuts import render, redirect, get_object_or_404
# from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F, ExpressionWrapper, Sum, FloatField
# from django.http import JsonResponse

from django.contrib.auth.decorators import login_required
# from django.http import HttpResponse
from .models import Cart, CartItem
from store.models import Product
from orders.models import Order
# Create your views here.

# getting the session_id
def _cart_id(request):
    # checking if session does not exist, then create it and return the session_id
    cart = request.session.session_key
    
    if not cart:
        request.session.create()
    return cart


def add_cart(request, product_id):
    # get the product id of the user. Use get() method instead of filtering it
    current_user = request.user
    product = get_object_or_404(Product, id=product_id)
    cart_id = _cart_id(request)
    
    if current_user.is_authenticated:
        if request.method == 'POST':            
            # now for the cart item. Which we will get the product and the cart id
            try:
                cart_item = CartItem.objects.get(product=product, user=current_user)
                cart_item.quantity += 1
                cart_item.save()
                    # this is removed, 
                    # return redirect('carts:cart')
                # this is for if it exists, then get it
            except CartItem.DoesNotExist:
                # if it does not exist, then create a new cart item with the quantity of one
                CartItem.objects.create(product=product, user=current_user, quantity=1)

            return redirect('carts:cart')
        return redirect('carts:cart')
    
    else:
        if request.method == 'POST':
            # get the sessionID of that user, if it does not exist, then create one for them
            try:
                cart = Cart.objects.get(cart_id=cart_id)
            except Cart.DoesNotExist:
                # if it does not exist, then create one for them
                cart = Cart.objects.create(cart_id=cart_id)
                
            
            # now for the cart item. Which we will get the product and the cart id
            try:
                cart_item = CartItem.objects.get(product=product, cart=cart)
                cart_item.quantity += 1
                cart_item.save()
                    # this is removed, 
                    # return redirect('carts:cart')
                # this is for if it exists, then get it
            except CartItem.DoesNotExist:
                # if it does not exist, then create a new cart item with the quantity of one
                CartItem.objects.create(product=product, cart=cart, quantity=1)

            return redirect('carts:cart')
        return redirect('carts:cart')
            

# making the remove button
def remove_cart(request, product_id, cart_item_id):
    # first we need to get the product id of the product we want to reduce
    product = get_object_or_404(Product, id=product_id)
    
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(user=request.user, product=product, id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(cart=cart, product=product, id=cart_item_id)
        
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except Cart.DoesNotExist:
        pass
    except CartItem.DoesNotExist:
        pass
    return redirect('carts:cart')


def remove_cart_item(request, product_id, cart_item_id):
    # get the product
    current_user = request.user
    product = get_object_or_404(Product, id=product_id)
    
    try:
        if current_user.is_authenticated:
            cart_item=CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
            
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item=CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
        
        if cart_item:
            cart_item.delete()
    except:
        pass
    return redirect('carts:cart')

def cart(request):
    cart_id = _cart_id(request)
    is_cart = request.path == ['/carts/']
    
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
            is_cart = True
        else:
            cart = Cart.objects.get(cart_id=cart_id)
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
            is_cart = True
        
        # Using the aggregate and annotate methods to directly calculate the total quantity and total price of what is in the user 
        total_quantity = cart_items.aggregate(Sum(F('quantity')))['quantity__sum'] or 0
        total_price = cart_items.aggregate(
            total_price=Sum(ExpressionWrapper(F('product__price') * F('quantity'), output_field=FloatField())))['total_price'] or 0
    except Cart.DoesNotExist:
        cart_items = []
        total_quantity = 0
        total_price = 0
        
    context = {
        'cart_items': cart_items,
        'total_quantity':total_quantity,
        'total_price':total_price,
        'is_cart':is_cart,
        
    }
    return render(request, 'carts/cart.html', context)



@login_required
def checkout(request):
    current_user = request.user
    cart_id = _cart_id(request)
    
    try:
        if current_user.is_authenticated:
            cart_items = CartItem.objects.filter(user=current_user)
        else:
            cart = Cart.objects.get(cart_id=cart_id)
            cart_items = CartItem.objects.filter(cart=cart)
        
        # Using the aggregate and annotate methods to directly calculate the total quantity and total price of what is in the user 
        total_quantity = cart_items.aggregate(Sum(F('quantity')))['quantity__sum'] or 0
        total_price = cart_items.aggregate(
            total_price=Sum(ExpressionWrapper(F('product__price') * F('quantity'), output_field=FloatField())))['total_price'] or 0
    except Cart.DoesNotExist:
        cart_items = []
        total_quantity = 0
        total_price = 0
        
    context = {
        'cart_items': cart_items,
        'total_quantity':total_quantity,
        'total_price':total_price,
        
    }
    return render(request, 'carts/checkout.html', context)


@login_required
def dashboard(request):
    orders = Order.objects.order_by('-created_at').filter(user=request.user.id, is_ordered=True)
    order_count = orders.count()
    
    context = {
        'orders':orders,
        'order_count':order_count
    }
    return render(request, 'carts/dashboard.html', context)