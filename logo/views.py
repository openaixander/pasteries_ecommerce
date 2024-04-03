from django.shortcuts import render
from .models import *

# Create your views here.
def index(request):
    carousel_descriptions = CarouselDescription.objects.all() 
    web_logo = Weblogo.objects.first()
    web_picture = WebPicture.objects.first()
    
    context = {
        'carousel_descriptions':carousel_descriptions,
        'web_logo':web_logo,
        'web_picture':web_picture
    }
    return render(request, 'logo/index.html', context)

def about_us(request):
    web_logo = Weblogo.objects.first()
    about_us = AboutMe.objects.all()
    
    context = {
        'web_logo':web_logo,
        'about_us':about_us
    }
    return render(request, 'logo/about_us.html', context)