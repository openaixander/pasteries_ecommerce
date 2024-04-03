from django.shortcuts import render, redirect
from django.db.models import F, ExpressionWrapper, Sum, FloatField

from django.template.loader import render_to_string
from django.core.mail import EmailMessage


from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph
from reportlab.lib import colors
from django.http import JsonResponse, HttpResponse
import json
import datetime
from .models import Order, Payment, OrderProduct
from store.models import Product
from .forms import OrderForm
from carts.models import CartItem
# Create your views here.




def place_order(request):
    current_user = request.user
    
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    
    if cart_count <= 0:
       return redirect('carts:checkout')
    total_quantity = cart_items.aggregate(Sum(F('quantity')))['quantity__sum'] or 0
    total_price = cart_items.aggregate(total_price=Sum(ExpressionWrapper(F('product__price') * F('quantity'), output_field=FloatField())))['total_price'] or 0
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        
        if form.is_valid():
            # store all the billing information inside the order table
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.city = form.cleaned_data['city']
            data.state = form.cleaned_data['state']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = total_price
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()
            
            # generate the orderID
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime(f"%d"))
            mt = int(datetime.date.today().strftime('%m'))
            
            d = datetime.date(yr, mt, dt)
            
            current_date = d.strftime(f"%Y%m%d")
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()
            
            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            context = {
                'order':order,
                'cart_items':cart_items,
                'total_price':total_price,
                'total_quantity':total_quantity
            }
            return render(request, 'orders/payments.html', context)
    else:
        return redirect('carts:checkout')
            
        

def payments(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            order = Order.objects.select_related('user').get(
                user=request.user,
                is_ordered=False,
                order_number=data.get('orderID')
            )
            payment = Payment.objects.create(
                user=request.user,
                payment_id=data.get('transID'),
                payment_method=data.get('payment_method'),
                amount_paid=order.order_total,
                status=data.get('status')
            )
            order.payment = payment
            order.is_ordered = True
            order.save()
            
            # move cart items to Order Product table
            cart_items = CartItem.objects.filter(user=request.user)
            
            for item in cart_items:
                orderproduct = OrderProduct()
                orderproduct.order_id = order.id
                orderproduct.payment = payment
                orderproduct.user_id = request.user.id
                orderproduct.product_id = item.product_id
                orderproduct.quantity = item.quantity
                orderproduct.product_price= item.product.price
                orderproduct.ordered =  True
                orderproduct.save()
            # Reduce the quantity of the product
                product = Product.objects.get(id=item.product_id)
                product.stock -= item.quantity
                product.save()
            
            # Clear the cart
            CartItem.objects.filter(user=request.user).delete()
            
            # Send order recieved email to customer
            mail_subject = 'Thank you for ordering.'
            context_string = {
                'user': request.user,
                'order': order,
            }
            message = render_to_string('orders/order_recieved_email.html', context_string)
            to_email = order.email
            send_mail = EmailMessage(mail_subject, message, to=[to_email])
            send_mail.send()
            
            # Send order number and transID back to sendData method via jsonresponse
            data_items = {
                'order_number': order.order_number,
                'transID':payment.payment_id,
            }
            return JsonResponse(data_items)
        except (Order.DoesNotExist, json.JSONDecodeError, KeyError):
            return JsonResponse({'success': False, 'message': 'Invalid request or order does not exist'}, status=400)
    else:
        return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)
    
    
def order_complete(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')
    
    
    try:
        # Retrieve the order
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        
        # Retrieve all order products related to the order
        order_products = OrderProduct.objects.filter(order_id=order.id)
        
        # Calculate the total price of all ordered products using aggregation
        total_ordered_products = order_products.aggregate(
            total_price=Sum(
                ExpressionWrapper(F('product__price') * F('quantity'), output_field=FloatField())
            )
        )['total_price'] or 0
        
        # Prepare the context to pass to the template
        context = {
            'order': order,
            'order_products': order_products,
            'total_ordered_products': total_ordered_products
        }
        
        # Render the template with the calculated total price
        return render(request, 'orders/order_complete.html', context)
    except(Order.DoesNotExist, OrderProduct.DoesNotExist):
        return redirect('logo:index')


def generate_pdf(request, order_id):
    order = Order.objects.get(id=order_id, is_ordered=True)
    order_products = OrderProduct.objects.filter(order_id=order.id)
    total_ordered_products = order_products.aggregate(
        total_price=Sum(ExpressionWrapper(F('product__price') * F('quantity'), output_field=FloatField()))
    )['total_price'] or 0

    # Create PDF document
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Set up styles
    style = getSampleStyleSheet()['Title']
    style.fontSize = 20

    # Add header message
    header_message = "Thank you for ordering from ShiShiCakes"
    p = Paragraph(header_message, style)
    p.wrapOn(pdf, width, height)
    p.drawOn(pdf, width / 2 - p.width / 2, height - inch)

    # Add content to PDF
    y_coordinate = height - 2 * inch  # Initial y-coordinate

    pdf.setFillColor(colors.blue)
    order_number_text = f"Order Number: {order.order_number}"
    pdf.drawString(width / 2 - pdf.stringWidth(order_number_text) / 2, y_coordinate, order_number_text)  # Order number

    y_coordinate -= 0.5 * inch  # Move to the next line
    pdf.setFillColor(colors.green)
    for order_product in order_products:
        product_name = order_product.product.product_name
        quantity = order_product.quantity
        product_info = f"{product_name}: {quantity}"
        pdf.drawString(width / 2 - pdf.stringWidth(product_info) / 2, y_coordinate, product_info)
        y_coordinate -= 0.3 * inch  # Move to the next line

    y_coordinate -= 0.5 * inch  # Move to the next line
    pdf.setFillColor(colors.black)
    payment_id_text = f"Payment ID: {order_products.first().payment.payment_id}" if order_products.exists() and order_products.first().payment else "Payment ID: N/A"
    pdf.drawString(width / 2 - pdf.stringWidth(payment_id_text) / 2, y_coordinate, payment_id_text)

    y_coordinate -= 0.5 * inch  # Move to the next line
    pdf.setFillColor(colors.red)
    total_text = f"Total: ₦{total_ordered_products}"
    pdf.drawString(width / 2 - pdf.stringWidth(total_text) / 2, y_coordinate, total_text)

    # Close PDF
    pdf.showPage()
    pdf.save()

    # Get PDF content and return as HTTP response
    pdf_content = buffer.getvalue()
    buffer.close()
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="order_summary.pdf"'
    response.write(pdf_content)

    return response
