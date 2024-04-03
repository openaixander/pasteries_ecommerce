from django.db import models
from django.urls import reverse
from cloudinary.models import CloudinaryField
# Create your models here.



# creating the category model, and the product model 

class Category(models.Model):
    category_name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    
    def get_url(self):
        return reverse('store:store', args=[self.slug])
    
    class Meta:
        verbose_name_plural = 'Categories'
    
    def __str__(self) -> str:
        return self.category_name
    
    
class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=100)
    description = models.TextField(max_length=500, blank=True, null=True)
    slug = models.SlugField(unique=True)
    price = models.IntegerField()
    image = CloudinaryField(folder='product', blank=True)
    stock = models.IntegerField()
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def get_product_url(self):
        return reverse('store:product_detail', args=[self.category.slug, self.slug])
    
    
    def __str__(self) -> str:
        if self.product_name:
            return str(self.product_name)
        else:
            return "Unnamed Product"