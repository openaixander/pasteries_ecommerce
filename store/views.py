from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, PageNotAnInteger, Page, EmptyPage
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .super_admin import superadmin_required
from .models import Category, Product
from .forms import CategoryForm
# Create your views here.


def store(request, category_id=None):
    is_store_page =request.path in ['/store/']
    products = Product.objects.filter(is_available=True).order_by('created_at')
    
    # let it filter whatevrer is in the product based on their flag
    # now check, if category_id exists on not
    
    if category_id:
        # then we get the category
        category = get_object_or_404(Category, slug=category_id)
        products = products.filter(category=category)
        is_store_page = False  # Set to False when a filter is applied
    else:
        # if there is no filter, then just show the all products and the search page
        category = None  # No category filter applied
        
        
    # Paging the products using pagination]
    paged_product = Paginator(products, 5)
    page_number = request.GET.get("page")
    # we use the try-except block to handle the for the empty page
    try:
        product_paged = paged_product.get_page(page_number)
    except EmptyPage:
        product_paged = paged_product.get_page(1)
        
    product_count = products.count()
    
    
    
    context = {
        'product_count':product_count,
        'is_store_page' : is_store_page,
        'products': product_paged,
    }
    return render(request, 'store/store.html', context)



def search_results(request):
    is_store_page =request.path in ['/store/']
    query = request.GET.get('keyword')
    products = Product.objects.filter(is_available=True).order_by('-created_at')
    
    if query:
        categories = Category.objects.filter(category_name__icontains=query)
        products = Product.objects.filter(Q(category__in=categories) | Q(product_name__icontains=query))
        is_store_page = True
        
    paginator = Paginator(products, 5)  # Show 5 products per page
    
    page_number = request.GET.get('page')
    try:
        product_page = paginator.page(page_number)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        product_page = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page of results.
        product_page = paginator.page(paginator.num_pages)
    
    product_count = products.count()
        
    
    context = {
        'product_count':product_count,
        'products':product_page,
        'is_store_page':is_store_page,
        'query':query,
    }
        
    return render(request, 'store/store.html', context)


def product_detail(request, category_id, product_id):
    # this should be the same for the store page
    try:
        category = Category.objects.get(slug=category_id)
        single_product = Product.objects.get(category=category, slug=product_id)
        product_url = single_product.get_product_url()
        is_product_detail = request.path == product_url
        
    except(Category.DoesNotExist, Product.DoesNotExist):
        single_product = None
        is_product_detail = None
        
    context = {
        'single_product':single_product,
        'is_product_detail':is_product_detail
    }
    

    return render(request, 'store/product_detail.html', context)



@login_required
@superadmin_required
def add_category(request):
    
    if request.method != 'POST':
      form = CategoryForm()
      
    else:
        form = CategoryForm(request.POST)
        if form.is_valid():
            data = Category()
            data.category_name = form.cleaned_data['category_name']
            data.slug = form.cleaned_data['category_name']
            data.save()
            return redirect('store:add_category')
    return render(request, 'store/add_category.html')


