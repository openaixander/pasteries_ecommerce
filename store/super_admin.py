from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.contrib import messages


def superadmin_required(view_func):
    """
    Decorator for views that checks that the user is a superadmin,
    redirecting to the login page if necessary.
    """
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_superadmin:
            # If the user is not a superadmin, redirect to the login page
            messages.error(request, "Please login with your superadmin email to access page.")
            return redirect('logo:index')  
        
        # If the user is a superadmin, check if there's a 'next' parameter in the URL
        next_url = request.GET.get('next')
        if next_url:
            # If 'next' parameter exists, redirect the user to that URL after logging in
            return redirect(next_url)
        
        # If there's no 'next' parameter, proceed to the original view
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view