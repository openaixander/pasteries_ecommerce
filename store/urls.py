from django.urls import path

from . import views


app_name = 'store'


urlpatterns = [
    path('', views.store, name='store'),
    path('category/<slug:category_id>/', views.store, name='store'),
    path('category/<slug:category_id>/<slug:product_id>/', views.product_detail, name='product_detail'),
    # making the search functionality
    path('search_results/', views.search_results, name='search_results'),
    
    # admin_level_urls
    path('add_category/', views.add_category, name='add_category')
    
]