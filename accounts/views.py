from django.shortcuts import render, redirect
from .models import Account
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.db.models import F, Sum
# from store.models import Product
from carts.models import Cart, CartItem
from carts.views import _cart_id

from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.contrib import messages

from .forms import RegistrationForm
import requests
# Create your views here.


def register(request):
    is_reg_page = request.path in ['/accounts/register/']

    if request.method != 'POST':
        form = RegistrationForm()
    else:
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # Process form data
            try:
                first_name = form.cleaned_data['first_name']
                last_name = form.cleaned_data['last_name']
                email = form.cleaned_data['email']
                phone_number = form.cleaned_data['phone_number']
                password = form.cleaned_data['password']
                
                username = email.split('@')[0]
                
                # Create the user account
                user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username, password=password)
                user.phone_number = phone_number
                user.save()
                
                # USER ACTIVATION
                current_site = get_current_site(request)
                mail_subject = 'Please activate your account.'
                context_string = {
                    'user': user,
                    'domain': current_site,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': default_token_generator.make_token(user)
                }
                message = render_to_string('accounts/account_verification_email.html', context_string)
                to_email = email
                send_mail = EmailMessage(mail_subject, message, to=[to_email])
                send_mail.send()
                
                # messages.success(request, f'Thank you for registering with us. We have sent a verification link to {email}.')
                return redirect('/accounts/login/?command=verification&email='+email)
                
            except Exception as e:
                # Handle exceptions
                messages.error(request, f'An error occurred during registration.')
                # Optionally log the error for further investigation
                # logger.error(f'Error during registration: {e}')
    
    context = {
        'is_reg_page': is_reg_page,
        'form': form
    }
    return render(request, 'accounts/registration.html', context)


def activate(request, uidb64, token):
    # first we have to decode the primary key of the user
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
        
    except(TypeError, ValueError, OverflowError):
        messages.error(request, 'Invalid activation link:The user ID is invalid.')
        return redirect('accounts:register')
    
    except Account.DoesNotExist:
        messages.error(request, 'Invalid activation link: User does not exist.')
        return redirect('accounts:register')
    
    if user.is_active:
        messages.warning(request, 'Your account has already been activated.')

    else:
        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.is_activation_completed = True
            user.save()
            messages.success(request, 'Congratulations! Your account has been activated')
            # return redirect('accounts:login')
        
        else:
            messages.error(request, 'Invalid activation link: The token is invalid.')
            return redirect('accounts:register')
    return redirect('accounts:login')


def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
    
        try:
            user = auth.authenticate(email=email, password=password)
    
            if user is not None:
               # Assigning the cart items to the authenticated user
                cart_id = _cart_id(request)
                try:
                    # Get the cart associated with the anonymous user (if any)
                    anonymous_cart = Cart.objects.get(cart_id=cart_id)
                    # Get cart items associated with the anonymous user
                    anonymous_cart_items = CartItem.objects.filter(cart=anonymous_cart)
                    
                    # Update or assign cart items to the authenticated user in the database
                    existing_cart_items = CartItem.objects.filter(
                        user=user,
                        product__in=anonymous_cart_items.values_list('product', flat=True)
                    )
                    
                    # Calculate the total quantity to update for existing cart items
                    total_quantity = anonymous_cart_items.aggregate(Sum('quantity'))['quantity__sum'] or 0
                    
                    # Update existing cart items with the total quantity
                    existing_cart_items.update(quantity=F('quantity') + total_quantity)
                    
                    # Exclude existing cart items from the anonymous cart items
                    new_cart_items = anonymous_cart_items.exclude(product__in=existing_cart_items.values_list('product', flat=True))
                    
                    # Assign new cart items to the authenticated user
                    new_cart_items.update(cart=None, user=user)
                    
                    # Delete the anonymous cart after merging
                    anonymous_cart.delete()
                except Cart.DoesNotExist:
                    pass


                auth.login(request, user)
                url = request.META.get('HTTP_REFERER')
                try:
                    if url:
                        query = requests.utils.urlparse(url).query
                        params = dict(x.split('=') for x in query.split('&'))
                        if 'next' in params:
                            next_page = params['next']
                            return redirect(next_page)
                except Exception as e:
                    pass

                # If 'next' parameter is not present or an error occurs, redirect to default page
                messages.success(request, f'Welcome {user.first_name}, you are logged in.')
                return redirect('carts:dashboard')
                
            else:
                messages.error(request, 'Invalid login credentials!')
                return redirect('accounts:login')
        except Exception as e:
            messages.error(request, 'An error occurred during login. Please try again later.')
            return redirect('accounts:login')
    
        
    return render(request, 'accounts/login.html')

@login_required()
def logout(request):
    auth.logout(request)
    messages.info(request, f'You have logged out. Visit us again.')
    return redirect('accounts:login')


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        
        # first we check, if the email is in the account model
        
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)
            
            # now we send a message to the user and encypting the data
            current_site = get_current_site(request)
            mail_subject = 'Please reset your password.'
            context_string = {
                'user':user,
                'domain':current_site,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':default_token_generator.make_token(user),
            }
            
            message = render_to_string('accounts/reset_password_email.html', context_string)
            to_mail = email
            send_mail = EmailMessage(mail_subject, message, to=[to_mail])
            send_mail.send()
            messages.success(request, 'Password reset link has been sent to your email address.')
            return redirect('accounts:login')
        else:
            messages.error(request, 'User does not exist!')
            return redirect('accounts:login')

    return render(request, 'accounts/forgot_password.html')


def reset_password_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
        
    except(TypeError, ValueError, OverflowError):
        messages.error(request, 'Invalid reset password link:The user ID is invalid.')
        return redirect('accounts:register')
    
    except Account.DoesNotExist:
        messages.error(request, 'Invalid reset password link: User does not exist.')
        return redirect('accounts:register')
        
    
    if user is not None and default_token_generator.check_token(user, token):
        # here we save the user ID in the session
        request.session['uid'] = uid
        messages.info(request, 'Reset your password.')
        return redirect('accounts:reset_password')
    
    else:
        messages.error(request, 'This link has expired!')
        return redirect('accounts:forgot_password')
    
    
def reset_password(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        if len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return redirect('accounts:reset_password')
        
        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return redirect('accounts:reset_password')
        
        try:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
        except Account.DoesNotExist:
            messages.error(request, 'Invalid user for password reset.')
            return redirect('accounts:register')
        
        user.set_password(password)
        user.save()
        messages.success(request, 'Password reset successful. You can now login with your new password.')
        return redirect('accounts:login')
    
    return render(request, 'accounts/reset_password.html')


@login_required
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']
        
        user = Account.objects.get(username__exact=request.user.username)
        
        if new_password == confirm_password:
            success = user.check_password(current_password)
            
            if success: 
                if len(new_password) >= 8:  # Check password length
                    user.set_password(new_password)
                    user.save()
                    auth.logout(request)  # Logout user
                    messages.success(request, 'Password updated successfully. You have been logged out.')
                    return redirect('accounts:login')
                else:
                    messages.error(request, 'Password must be at least 8 characters long.')
            else:
                messages.error(request, 'Please enter valid current password')
        else:
            messages.error(request, 'Password does not match!')
    
    return render(request, 'accounts/change_password.html')
